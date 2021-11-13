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

        return render_template(
            "geometry_new.html", error=error, description=request.form["description"]
        )


@GEOMETRY_BLUEPRINT.route("", methods=["GET"])
def list_geometries():
    # geometries = geometry_service.get_geometries()
    geometries = [
        {
            "id": "1",
            "description": "la descript",
            "user": {"name": "Juan", "lastname": "Perez"},
            "created_at": "2020/2020/2020",
        }
    ]
    response_list = []
    for geometry in geometries:
        geometry_row = {
            "id": str(geometry["id"]),
            "description": geometry["description"],
            "user": geometry["user"]["name"] + " " + geometry["user"]["lastname"],
            "created_at": geometry["created_at"],
        }
        response_list.append(geometry_row)

    print("respondo " + str({"items": response_list}))
    return jsonify({"items": response_list})
