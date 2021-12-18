from flask import Blueprint, redirect, url_for, jsonify

from src import logger
from src.service import execution_plan_service

EXECUTION_PLAN_BLUEPRINT = Blueprint("execution_plan_controller", __name__)


@EXECUTION_PLAN_BLUEPRINT.route("", methods=["POST"])
def save():
    geometry = None
    logger.info(
        "Geometry created with id: " + str(geometry.id) + " for file: " + geometry.name
    )

    return redirect(url_for("view_controller.geometry_new"))


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
            "start_datetime": execution_plan.start_datetime,
            "end_datetime": execution_plan.end_datetime,
            "status": execution_plan.status,
        }
        response_list.append(execution_plan_row)

    return jsonify({"rows": response_list, "total": len(response_list)})
