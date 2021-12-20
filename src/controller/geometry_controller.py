from flask import Blueprint, request, render_template, jsonify

from src import logger
from src.service import geometry_service
from src.service.exception.file_exception import FileUploadError
from src.view.view_message import ViewMessage

GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)


@GEOMETRY_BLUEPRINT.route("", methods=["POST"])
def save():
    try:
        geometry = geometry_service.create(request)
        success = ViewMessage("Geometría #" + str(geometry.id) + " creada con éxito.")
        return render_template("geometry_list.html", success=success)
    except FileUploadError as file_error:
        logger.error(file_error.message, file_error)
        error = ViewMessage("Error cargando archivo. Intente nuevamente.")

        return render_template("geometry.html", error=error, **request.form)


@GEOMETRY_BLUEPRINT.route("", methods=["GET"])
def list_geometries():
    geometries = geometry_service.get_geometries()

    response_list = []
    for geometry in geometries:
        user = geometry.user
        geometry_row = {
            "id": geometry.id,
            "name": geometry.name,
            "description": geometry.description,
            "user": user.fullname,
            "created_at": geometry.created_at.date(),
        }
        response_list.append(geometry_row)

    return jsonify({"rows": response_list, "total": len(response_list)})
