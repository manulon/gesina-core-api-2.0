from flask import Blueprint, render_template, request, redirect, url_for, current_app
from src.service import geometry_service

GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)


@GEOMETRY_BLUEPRINT.route("/")
@GEOMETRY_BLUEPRINT.route("")
def new():
    return render_template("new_geometry.html")


@GEOMETRY_BLUEPRINT.route("/", methods=["POST"])
@GEOMETRY_BLUEPRINT.route("", methods=["POST"])
def save():
    geometry = geometry_service.create(request)
    current_app.logger.info(
        "Geometry created with id: " + str(geometry.id) + " for file: " + geometry.name
    )

    return redirect(url_for("geometry_controller.new"))
