from flask import request, jsonify, Blueprint

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

@SCHEDULE_API_BLUEPRINT.delete("/<scheduled_task_id>")
def delete_scheduled_task(scheduled_task_id):
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

@SCHEDULE_API_BLUEPRINT.patch("/<scheduled_task_id>")
def edit_scheduled_task(scheduled_task_id):
    try:
        body = request.get_json()
        params = {
            'frequency': body.get('frequency'),
            'calibration_id': body.get('calibration_id'),
            'calibration_id_for_simulations': body.get('calibration_id_for_simulations'),
            'name': body.get('name'),
            'description': body.get('description'),
            'geometry_id': body.get('geometry_id'),
            'start_datetime': body.get('start_datetime'),
            'enabled': body.get('enabled'),
            'observation_days': body.get('observation_days'),
            'forecast_days': body.get('forecast_days'),
            'start_condition_type': body.get('start_condition_type'), # Initial flow or restart file
            'border_conditions': body.get('border_conditions'),
            'plan_series_list': body.get('plan_series_list')
        }
        schedule_task_service.update_from_json(scheduled_task_id, **params)
        response = jsonify({"message": f"Scheduled task with id {scheduled_task_id} edited successfully"})
        response.status_code = 200
    except KeyError as ke:
        response = jsonify({"message": f"Error editing scheduled task {scheduled_task_id}", "error": str(ke)})
        response.status_code = 400
    except Exception as e:
        response = jsonify({"message": f"Error editing scheduled task {scheduled_task_id}", "error": str(e)})
        response.status_code = 400
    return response
    
    
    
