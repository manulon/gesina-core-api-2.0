from flask import request, jsonify, Blueprint

from src.logger import get_logger
from src.exception.delete_geometry_exception import GeometryInUseException
from src.service import (
    geometry_service,
    api_authentication_service
)
from src.persistance.schemas import GEOMETRY_SCHEMA

GEOMETRY_API_BLUEPRINT = Blueprint("geometry", __name__, url_prefix="/geometry")

@GEOMETRY_API_BLUEPRINT.post("/")
def create_geometry():
    try:
        file = request.files.getlist('file')
        if len(file) == 0:
            raise ValueError("Please upload at least one file")
        if len(file) > 1:
            raise ValueError("Only one file allowed")
        if not file[0].filename or file[0].filename == '':
            raise ValueError("Incomplete geometry data provided: upload file")

        geometry = geometry_service.create(
            file[0].filename,
            file[0],
            "Creada usando API",
            api_authentication_service.get_current_user()
        )
        
        return { "file": geometry.name , "id": geometry.id}
    
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response

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
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({"error": f"Error while getting geometry: {str(e)}"})
        response.status_code = 400
        return response
    
@GEOMETRY_API_BLUEPRINT.get("/all")
def get_geometries():
    try:
        geometries = geometry_service.get_geometries()

        if geometries is None:
            response = jsonify({"error": "There are no geometries available"})
            response.status_code = 404
            return response

        response = jsonify(
            GEOMETRY_SCHEMA.dump(
                geometries, many=True
            )
        )
        response.status_code = 200
        return response
    
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({"error": f"Error while getting geometries: {str(e)}"})
        response.status_code = 400
        return response
    
@GEOMETRY_API_BLUEPRINT.delete("/<geometry_id>")
def delete_geometry(geometry_id):
    try:
        geometry_service.delete_geometry(geometry_id)
        response = jsonify({"message": "Geometry with id " + geometry_id + " deleted successfully"})
        response.status_code = 200
        return response
    except GeometryInUseException as dge:
        logger.error(dge)
        response = jsonify({"message": str(dge)})
        response.status_code = dge.status_code
        return response
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({"message": "error deleting geometry " + geometry_id,
                            "error": str(e)})
        response.status_code = 400
        return response
    
@GEOMETRY_API_BLUEPRINT.patch("/<geometry_id>")
def edit_geometry(geometry_id):
    try:
        body = request.get_json()
        description = body.get("description")

        geometry_service.edit_geometry(
            geometry_id, 
            description
        )
        return jsonify({"message": f"successfully edited geometry with id: {geometry_id}"})
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({"message": "error deleting editing plan " + geometry_id,
                            "error": str(e)})
        response.status_code = 400
        return response
    
    