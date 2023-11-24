from io import BytesIO

from flask import Blueprint, jsonify, send_file, url_for, redirect
from src import logger

from src.login_manager import user_is_authenticated
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service import execution_plan_service, file_storage_service, list_utils_service
from src.service.file_storage_service import FileType

EXECUTION_PLAN_BLUEPRINT = Blueprint("execution_plan_controller", __name__)
EXECUTION_PLAN_BLUEPRINT.before_request(user_is_authenticated)


@EXECUTION_PLAN_BLUEPRINT.route("", methods=["GET"])
def list_execution_plans():
    offset, limit = list_utils_service.process_list_params()
    execution_plans = execution_plan_service.get_execution_plans()
    total_rows = len(execution_plans)

    response_list = []
    for execution_plan in execution_plans[offset : offset + limit]:
        user = execution_plan.user
        execution_plan_row = {
            "id": execution_plan.id,
            "plan_name": execution_plan.plan_name,
            "user": user.full_name,
            "created_at": execution_plan.created_at.strftime("%d/%m/%Y"),
            "status": execution_plan.status,
        }
        response_list.append(execution_plan_row)

    return jsonify({"rows": response_list, "total": total_rows})


@EXECUTION_PLAN_BLUEPRINT.route("/download/<_id>/<_file_type>/<_file>")
def download(_id, _file_type, _file):
    with file_storage_service.get_file_by_type(
        FileType(_file_type), f"{_id}/{_file}"
    ) as file_from_storage:
        file = BytesIO(file_from_storage.data)

    return send_file(file, attachment_filename=_file)


@EXECUTION_PLAN_BLUEPRINT.route("/<execution_id>", methods=["POST"])
def update(execution_id):
    from src.tasks import queue_or_fake_simulate

    try:
        execution_plan_service.update_execution_plan_status(
            execution_id, ExecutionPlanStatus.RUNNING
        )
        queue_or_fake_simulate(execution_id)
        return redirect(url_for("view_controller.execution_plan_list"))
    except Exception as e:
        logger.error(e)
        raise e

@EXECUTION_PLAN_BLUEPRINT.route("cancel/<execution_id>", methods=["POST"])
def cancel(execution_id):
    from src.tasks import cancel_simulation

    try:
        cancel_simulation(execution_id)
        return redirect(url_for("view_controller.execution_plan_list"))
    except Exception as e:
        logger.error(e)
        raise e
