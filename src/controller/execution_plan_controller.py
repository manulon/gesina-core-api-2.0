from flask import Blueprint, jsonify, render_template, request

from src import logger
from src.service import execution_plan_service
from src.view.view_message import ViewMessage

EXECUTION_PLAN_BLUEPRINT = Blueprint("execution_plan_controller", __name__)


@EXECUTION_PLAN_BLUEPRINT.route("", methods=["POST"])
def save():
    logger.error("request: " + str(request.form))
    logger.error("request: " + str(request.files))
    success = ViewMessage("Simulacion dummy creada con éxito.")

    return render_template("execution_plan_list.html", success=success)


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
            "user": user.fullname,
            "execution_datetime": execution_plan.execution_datetime.date(),
            "status": execution_plan.status,
        }
        response_list.append(execution_plan_row)

    return jsonify({"rows": response_list, "total": len(response_list)})
