from flask import request, jsonify, Blueprint
from src.controller.schemas import SCHEDULE_TASK_SCHEMA
from src.service import schedule_task_service, list_utils_service, api_authentication_service
from src.service.border_series_service import retrieve_series, retrieve_series_json
from src.service.initial_flow_service import create_initial_flows, create_initial_flows_from_form, \
    create_initial_flows_from_json
from src.service.plan_series_service import retrieve_plan_series, retrieve_plan_series_json
from src.view.forms.schedule_config_form import SeriesForm

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


@SCHEDULE_API_BLUEPRINT.post("/")
def create_scheduled_task():
    body = request.get_json()
    params = {
        "frequency": body.get("frequency"),
        "calibration_id": body.get("calibration_id"),
        "calibration_id_for_simulations": body.get("calibration_id_for_simulations"),
        "enabled": body.get("enabled"),
        "name": body.get("name"),
        "description": body.get("description"),
        "geometry_id": body.get("geometry_id"),
        "start_datetime": body.get("start_datetime"),
        "start_condition_type": body.get("start_condition_type"),
        "observation_days": body.get("observation_days"),
        "forecast_days": body.get("forecast_days"),
        "user": api_authentication_service.get_current_user(),
        "border_conditions": retrieve_series_json(body.get("series_list_file")),
        "plan_series_list": retrieve_plan_series_json(body.get("plan_series_file"), body.get("plan_series_list")),
    }
    if body.get("start_condition_type") == "initial_flows":
        params["initial_flows"] = create_initial_flows_from_json(body.get("start_condition_type"),
                                                                 body.get("initial_flow_file"),
                                                                 body.get("initial_flow_list"))
    schedule_task_service.create()
    return jsonify({"message": "ok"})
