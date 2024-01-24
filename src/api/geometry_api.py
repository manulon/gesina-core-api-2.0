import io

from flask import request, jsonify, Blueprint

from src import logger
from src.persistance.geometry import Geometry
from src.service import (
    geometry_service,
    file_storage_service,
)
from src.service.file_storage_service import FileType

GEOMETRY_API_BLUEPRINT = Blueprint("geometry", __name__, url_prefix="/geometry")

@GEOMETRY_API_BLUEPRINT.get("/<geometry_id>")
def get_geometry(geometry_id):
    try:
        geometry = geometry_service.get_geometry(geometry_id)
        if geometry is None:
            response = jsonify({"error": f"Geometry {geometry_id} does not exist"})
            response.status_code = 404
            return response
                        
        geometry_dict = {
            "id": geometry.id,
            "name": geometry.name,
            "description": geometry.description,
            "created_at": geometry.created_at.isoformat(),
            "user_id": geometry.user_id,
            "user": geometry.user.full_name if geometry.user else None
        }

        response = jsonify(geometry_dict)
        response.status_code = 200
        return response
    
    except Exception as e:
        response = jsonify({"error": f"Error while getting geometry: {str(e)}"})
        response.status_code = 400
        return response
    
@GEOMETRY_API_BLUEPRINT.delete("/<geometry_id>")
def delete_execution_plan(geometry_id):
    try:
        geometry_service.delete_geometry(geometry_id)
        response = jsonify({"message": "Geometry with id " + geometry_id + " deleted successfully"})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({"message": "error deleting geometry " + geometry_id,
                            "error": str(e)})
        response.status_code = 400
        return response