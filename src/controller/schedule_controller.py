from io import BytesIO

from flask import Blueprint, jsonify, send_file

from src.login_manager import user_is_authenticated
from src.service import schedule_task_service, list_utils_service, file_storage_service, user_service
from src.persistance.schemas import SCHEDULE_TASK_SCHEMA
from src.service.file_storage_service import FileType

SCHEDULE_TASK_BLUEPRINT = Blueprint("schedule_controller", __name__)
SCHEDULE_TASK_BLUEPRINT.before_request(user_is_authenticated)


@SCHEDULE_TASK_BLUEPRINT.route("", methods=["GET"])
def list_schedule_tasks():
    offset, limit = list_utils_service.process_list_params()
    schedule_tasks = schedule_task_service.get_schedule_tasks(reduced=True)
    total_rows = len(schedule_tasks)
    schedule_tasks = SCHEDULE_TASK_SCHEMA.dump(
                schedule_tasks[offset : offset + limit], many=True
            )
    for task in schedule_tasks:
        task["user_name"] = user_service.get_user(task["user_id"]).full_name

    return jsonify(
        {
            "rows": schedule_tasks,
            "total": total_rows,
        }
    )


@SCHEDULE_TASK_BLUEPRINT.route("/download/<_id>/<_file_name>")
def download(_id, _file_name):
    with file_storage_service.get_file_by_type(
        FileType.SCHEDULED_TASK, f"{_id}/{_file_name}"
    ) as file_from_storage:
        file = BytesIO(file_from_storage.data)

    return send_file(file, attachment_filename=_file_name)

@SCHEDULE_TASK_BLUEPRINT.route("/<scheduled_task_id>", methods=["DELETE"])
def delete(scheduled_task_id):
    try:
        schedule_task_service.delete_scheduled_task(scheduled_task_id)
        response = jsonify({"message": "Scheduled task with id " + scheduled_task_id + " deleted successfully"})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({"message": "error deleting geometry " + scheduled_task_id,
                            "error": str(e)})
        response.status_code = 400
        return response

@SCHEDULE_TASK_BLUEPRINT.route("/copy/<id>", methods=["POST"])
def copy(id):
    try:
        schedule_task = schedule_task_service.copy_schedule_task(id)
        response = jsonify({"message": "Scheduled task with id " + id + " copied successfully"})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({"message": "error copying geometry " + id,
                            "error": str(e)})
        response.status_code = 400
        return response