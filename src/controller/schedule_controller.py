from flask import Blueprint, jsonify

from src.login_manager import user_is_authenticated
from src.service import schedule_task_service
from src.controller.schemas import SCHEDULE_TASK_SCHEMA

SCHEDULE_TASK_BLUEPRINT = Blueprint("schedule_controller", __name__)
SCHEDULE_TASK_BLUEPRINT.before_request(user_is_authenticated)


@SCHEDULE_TASK_BLUEPRINT.route("", methods=["GET"])
def list_schedule_tasks():
    schedule_tasks = schedule_task_service.get_schedule_tasks()
    return jsonify(
        {
            "rows": SCHEDULE_TASK_SCHEMA.dump(schedule_tasks, many=True),
            "total": len(schedule_tasks),
        }
    )
