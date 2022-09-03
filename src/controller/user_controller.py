from flask import Blueprint, jsonify

from src.controller.schemas import USER_SCHEMA
from src.login_manager import user_is_authenticated
from src.service import user_service

USER_BLUEPRINT = Blueprint("user_controller", __name__)
USER_BLUEPRINT.before_request(user_is_authenticated)


@USER_BLUEPRINT.route("", methods=["GET"])
def list_users():
    schedule_tasks = user_service.get_all_users()
    return jsonify(
        {
            "rows": USER_SCHEMA.dump(schedule_tasks, many=True),
            "total": len(schedule_tasks),
        }
    )
