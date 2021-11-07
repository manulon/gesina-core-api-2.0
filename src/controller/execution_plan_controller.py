from flask import Blueprint, render_template, request, redirect, url_for, current_app
from src.service import geometry_service

EXECUTION_PLAN_BLUEPRINT = Blueprint("execution_plan_controller", __name__)


@EXECUTION_PLAN_BLUEPRINT.route("/", methods=["POST"], defaults={"path": ""})
def save():
    current_app.logger.info(
        "Geometry created with id: " + str(geometry.id) + " for file: " + geometry.name
    )

    return redirect(url_for("view_controller.geometry_new"))
