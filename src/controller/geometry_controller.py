from flask import Blueprint, jsonify

from src.login_manager import user_is_authenticated
from src.service import geometry_service

GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)
GEOMETRY_BLUEPRINT.before_request(user_is_authenticated)


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
            "user": user.full_name,
            "created_at": geometry.created_at.strftime("%d/%m/%Y"),
        }
        response_list.append(geometry_row)

    return jsonify({"rows": response_list, "total": len(response_list)})
