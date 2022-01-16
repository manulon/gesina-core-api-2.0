import sqlalchemy
from flask import Blueprint, render_template, jsonify

from src import logger
from src.service import geometry_service
from src.service.exception.file_exception import FileUploadError
from src.view.forms.geometry_form import GeometryForm

GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)


@GEOMETRY_BLUEPRINT.route("", methods=["POST"])
def save():
    form = GeometryForm()
    form.user_id.data = (
        1 if form.user_id.data is None else form.user_id.data
    )  # HARDCODED
    try:
        if form.validate_on_submit():
            geometry = geometry_service.create(form)
            success_message = f"Geometría #{str(geometry.id)} creada con éxito."
            return render_template("geometry_list.html", success=success_message)

        return render_template("geometry.html", form=form, errors=form.get_errors())
    except sqlalchemy.exc.IntegrityError as database_error:
        logger.error(database_error)
        error_message = "Error guardando información en la base de datos."

        return render_template("geometry.html", form=form, errors=[error_message])
    except FileUploadError as file_error:
        logger.error(file_error.message)
        error_message = "Error cargando archivo. Intente nuevamente."

        return render_template("geometry.html", form=form, errors=[error_message])


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
            "created_at": geometry.created_at.strftime("%d/%m/%Y"),
        }
        response_list.append(geometry_row)

    return jsonify({"rows": response_list, "total": len(response_list)})
