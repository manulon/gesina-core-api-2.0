import io

from flask import request, jsonify, Blueprint

from src import logger
from src.persistance.user import User
from src.service import (
    user_service,
    api_authentication_service
)

USER_API_BLUEPRINT = Blueprint("user", __name__, url_prefix="/user")

@USER_API_BLUEPRINT.post("/")
def create_user():
    try:
        body = request.get_json()

        user = user_service.save(
            body.get("email"),
            body.get("first_name"),
            body.get("last_name"),
            body.get("admin_role"),
            body.get("password"),
        )

        return {"new_user": user.id}
    
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response

@USER_API_BLUEPRINT.get("/<user_id>")
def get_user(user_id):
    try:
        user = user_service.get_user(user_id)

        if user:
            return {
                "email": user.email, 
                "first_name": user.first_name, 
                "last_name": user.last_name,
                "admin_role": user.admin_role,
                "active": user.active
            }
    
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response
    
@USER_API_BLUEPRINT.patch("/enable_disable/<user_id>")
def enable_disable_user(user_id):
    try:
        user = user_service.enable_disable_user(user_id)

        if user.active:
            return {"User enabled": user.id}
        else:
            return {"User disabled": user.id} 
    
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response
    
@USER_API_BLUEPRINT.patch("/<user_id>")
def edit_user(user_id):
    try:
        body = request.get_json()
        user_service.edit(
            user_id,
            body.get("email"),
            body.get("first_name"),
            body.get("last_name"),
            body.get("admin_role"),
            body.get("password")
        )
        return jsonify({"message": f"successfully edited user with id: {user_id}"})
    
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response




