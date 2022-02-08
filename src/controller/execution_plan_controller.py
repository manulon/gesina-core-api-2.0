from io import BytesIO

from flask import Blueprint, jsonify, send_file

from src.login_manager import user_is_authenticated
from src.service import execution_plan_service, file_storage_service

EXECUTION_PLAN_BLUEPRINT = Blueprint("execution_plan_controller", __name__)
EXECUTION_PLAN_BLUEPRINT.before_request(user_is_authenticated)


@EXECUTION_PLAN_BLUEPRINT.route("", methods=["GET"])
def list_execution_plans():
    execution_plans = execution_plan_service.get_execution_plans()

    response_list = []
    for execution_plan in execution_plans:
        user = execution_plan.user
        geometry = execution_plan.geometry
        execution_plan_row = {
            "id": execution_plan.id,
            "geometry": geometry.description,
            "user": user.full_name,
            "created_at": execution_plan.created_at.strftime("%d/%m/%Y"),
            "status": execution_plan.status,
        }
        response_list.append(execution_plan_row)

    return jsonify({"rows": response_list, "total": len(response_list)})


@EXECUTION_PLAN_BLUEPRINT.route("/download/<_id>/<_file>")
def download(_id, _file):
    file = BytesIO(file_storage_service.get_execution_file(f"{_id}/{_file}").data)
    return send_file(file, attachment_filename=_file)
