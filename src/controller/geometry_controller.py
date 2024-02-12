from io import BytesIO

from flask import Blueprint, jsonify, send_file, request, redirect, url_for
from src.exception.delete_geometry_exception import GeometryInUseException

from src.login_manager import user_is_authenticated
from src.service import geometry_service, file_storage_service, list_utils_service
from src.service.file_storage_service import FileType

GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)
GEOMETRY_BLUEPRINT.before_request(user_is_authenticated)


@GEOMETRY_BLUEPRINT.route("", methods=["GET"])
def list_geometries():
    offset, limit = list_utils_service.process_list_params()
    geometries = geometry_service.get_geometries()
    total_rows = len(geometries)

    response_list = []
    for geometry in geometries[offset : offset + limit]:
        user = geometry.user
        geometry_row = {
            "id": geometry.id,
            "name": geometry.name,
            "description": geometry.description,
            "user": user.full_name,
            "created_at": geometry.created_at.strftime("%d/%m/%Y"),
        }
        response_list.append(geometry_row)

    return jsonify({"rows": response_list, "total": total_rows})

@GEOMETRY_BLUEPRINT.route("/download/<_id>")
def download(_id):
    geometry = geometry_service.get_geometry(_id)
    with file_storage_service.get_file_by_type(
        FileType.GEOMETRY, geometry.name
    ) as file_from_storage:
        file = BytesIO(file_from_storage.data)

    return send_file(file, attachment_filename=geometry.name)

@GEOMETRY_BLUEPRINT.route("/<geometry_id>", methods=["DELETE"])
def delete(geometry_id):
    try:
        geometry_service.delete_geometry(geometry_id)
        response = jsonify({"message": "Geometry with id " + geometry_id + " deleted successfully"})
        response.status_code = 200
        return response
    except GeometryInUseException as dge:
        response = jsonify({"message": str(dge)})
        response.status_code = dge.status_code
        return response
    except Exception as e:
        response = jsonify({"message": "error deleting geometry " + geometry_id,
                            "error": str(e)})
        response.status_code = 400
        return response
    
@GEOMETRY_BLUEPRINT.route("/<geometry_id>", methods=["POST"])
def edit_geometry(geometry_id):
    try:
        geometry_id = request.form.get("geometry_id")
        description = request.form.get("description")

        geometry_service.edit_geometry(
            geometry_id,
            description
        )

        return redirect(url_for('view_controller.geometry_list', edit_success=geometry_id))
    except Exception as e:
        return redirect(url_for('view_controller.geometry_list', edit_failed=geometry_id))
