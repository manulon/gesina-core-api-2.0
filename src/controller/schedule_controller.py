from io import BytesIO

from flask import Blueprint, jsonify, send_file

from src.login_manager import user_is_authenticated
from src.service import schedule_task_service, list_utils_service, file_storage_service
from src.controller.schemas import SCHEDULE_TASK_SCHEMA
from src.service.file_storage_service import FileType

SCHEDULE_TASK_BLUEPRINT = Blueprint("schedule_controller", __name__)
SCHEDULE_TASK_BLUEPRINT.before_request(user_is_authenticated)


@SCHEDULE_TASK_BLUEPRINT.route("", methods=["GET"])
def list_schedule_tasks():
    offset, limit = list_utils_service.process_list_params()
    schedule_tasks = schedule_task_service.get_schedule_tasks()
    total_rows = len(schedule_tasks)

    return jsonify(
        {
            "rows": SCHEDULE_TASK_SCHEMA.dump(
                schedule_tasks[offset : offset + limit], many=True
            ),
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
