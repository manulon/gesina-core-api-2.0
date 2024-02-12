from flask import Blueprint, jsonify

from src.controller.schemas import SCHEDULE_TASK_SCHEMA
from src.service import schedule_task_service, list_utils_service

SCHEDULE_API_BLUEPRINT = Blueprint("scheduled_task", __name__, url_prefix="/schedule_task")


@SCHEDULE_API_BLUEPRINT.get("/<scheduled_task_id>")
def get_scheduled_task(scheduled_task_id):
    task = schedule_task_service.get_schedule_task_config(scheduled_task_id)
    obj = SCHEDULE_TASK_SCHEMA.dump(task)
    return jsonify(obj)


@SCHEDULE_API_BLUEPRINT.get("/all")
def list_schedule_tasks():
    schedule_tasks = schedule_task_service.get_schedule_tasks()

    return jsonify(
        SCHEDULE_TASK_SCHEMA.dump(
            schedule_tasks, many=True
        )
    )
