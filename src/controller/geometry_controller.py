from flask import Blueprint, request, render_template

from src import logger
from src.service import geometry_service
from src.service.exception.file_exception import FileUploadError
from src.view.view_message import ViewMessage

GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)


@GEOMETRY_BLUEPRINT.route("", methods=["POST"])
def save():
    try:
        geometry = geometry_service.create(request)
        success = ViewMessage("Geometría #" + geometry.id + " creada con éxito.")
        return render_template("geometry_list.html", success=success)
    except FileUploadError as file_error:
        logger.error(file_error.message, file_error)
        error = ViewMessage("Error cargando archivo. Intente nuevamente.")

        return render_template(
            "geometry_new.html", error=error, description=request.form["description"]
        )
