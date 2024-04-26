from flask import request, jsonify, Blueprint

from src.api.utils import validate_fields
from src.controller.schemas import SCHEDULE_TASK_SCHEMA
from src.logger import get_logger
from src.service import schedule_task_service, api_authentication_service, file_storage_service
from src.service.border_series_service import forecast_and_observation_values_exists_json, retrieve_series_json
from src.service.exception.file_exception import FileUploadError
from src.service.initial_flow_service import create_initial_flows_from_json
from src.service.plan_series_service import check_duplicate_output_series_json, retrieve_plan_series_json
from src.service.file_storage_service import FileType

SCHEDULE_API_BLUEPRINT = Blueprint("scheduled_task", __name__, url_prefix="/schedule_task")


@SCHEDULE_API_BLUEPRINT.get("/<scheduled_task_id>")
def get_scheduled_task(scheduled_task_id):
    try:
        if not scheduled_task_id.isnumeric():
            raise Exception("Id is not numeric")
        task = schedule_task_service.get_schedule_task_config(scheduled_task_id)
        if not task:
            raise Exception(f"Scheduled task with id {scheduled_task_id} not found")
        obj = SCHEDULE_TASK_SCHEMA.dump(task)
        if request.args.get("with_files") == "true":
            files = file_storage_service.get_scheduled_task_files(scheduled_task_id)
            obj["files"] = files
        return jsonify(obj)
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({
            "message": f"bad request while getting scheduled task {scheduled_task_id}",
            "error": str(e)
        })
        response.status_code = 400
        return response


@SCHEDULE_API_BLUEPRINT.get("/tasks")
def list_schedule_tasks():
    try:
        args = request.args
        schedule_tasks = schedule_task_service.get_schedule_tasks(args.get("name"),
                                                                  args.get('user_first_name'),
                                                                  args.get('user_last_name'),
                                                                  args.get('start_condition_type'),
                                                                  args.get('date_from'),
                                                                  args.get('date_to'),
                                                                  args.get('enabled'),
                                                                  args.get('frequency'),
                                                                  args.get('calibration_id'),
                                                                  args.get('calibration_id_for_simulations'))

        return jsonify(
            SCHEDULE_TASK_SCHEMA.dump(
                schedule_tasks, many=True
            )
        )
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({
            "message": "bad request while retrieving scheduled tasks",
            "error": str(e)
        })
        response.status_code = 400
        return response


@SCHEDULE_API_BLUEPRINT.delete("/<scheduled_task_id>")
def delete_scheduled_task(scheduled_task_id):
    try:
        schedule_task_service.delete_scheduled_task(scheduled_task_id)
        response = jsonify({"message": "Scheduled task with id " + scheduled_task_id + " deleted successfully"})
        response.status_code = 200
        return response
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
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
            'start_condition_type': body.get('start_condition_type'),  # Initial flow or restart file
            'border_conditions': body.get('border_conditions'),
            'plan_series_list': body.get('plan_series_list'),
            'initial_flows': body.get('initial_flows')
        }

        scheduled_config = schedule_task_service.get_schedule_task_config(scheduled_task_id)
        if not scheduled_config:
            raise Exception(f"Scheduled task with id {scheduled_task_id} not found")

        if params["enabled"]:
            if len(params["border_conditions"]) == 0 and len(scheduled_config.border_conditions) == 0:
                return send_bad_request("There must be at least one border condition set to enable the scheduled "
                                        "task.")
        if len(params["border_conditions"]) != 0:
            if not params['observation_days'] and not scheduled_config.observation_days:
                return send_bad_request("observation_days must be set")

            if not params['forecast_days'] and not scheduled_config.forecast_days:
                return send_bad_request("forecast_days must be set")

            if not params['calibration_id'] and not scheduled_config.calibration_id:
                return send_bad_request("calibration_id must be set")

            observation_days = params['observation_days'] if params[
                'observation_days'] else scheduled_config.observation_days
            forecast_days = params['forecast_days'] if params['forecast_days'] else scheduled_config.forecast_days
            calibration_id = params['calibration_id'] if params[
                'calibration_id'] else scheduled_config.calibration_id

            exists_forecast_and_observation_values = forecast_and_observation_values_exists_json(
                params["border_conditions"], observation_days, forecast_days,
                calibration_id)

            if not exists_forecast_and_observation_values:
                return send_bad_request(f'The scheduled task could not be created due to the absence of a boundary '
                                        f'series in the INA database for the calibration ID {str(calibration_id)} and'
                                        f' series id {params["border_conditions"][0].get("series_id")} ')

        duplicate_output_series, duplicate_key = check_duplicate_output_series_json(params["plan_series_list"],
                                                                                    scheduled_config)

        if duplicate_output_series:
            return send_bad_request(
                'The output series (' + duplicate_key[0] + ', ' + duplicate_key[1] + ', ' + duplicate_key[
                    2] + ') is duplicated. The scheduled task run can not be created.')

        schedule_task_service.update_from_json(scheduled_task_id, **params)
        response = jsonify({"message": f"Scheduled task with id {scheduled_task_id} edited successfully"})
        response.status_code = 200
    except FileUploadError as file_error:
        logger = get_logger()
        logger.error(file_error, exc_info=True)
        response = jsonify(
            {"message": f"You must upload all the required files to enable execution", "error": str(file_error)})
        response.status_code = 400
    except KeyError as ke:
        logger = get_logger()
        logger.error(ke, exc_info=True)
        response = jsonify({"message": f"Error editing scheduled task {scheduled_task_id}", "error": str(ke)})
        response.status_code = 400
    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({"message": f"Error editing scheduled task {scheduled_task_id}", "error": str(e)})
        response.status_code = 400
    return response


@SCHEDULE_API_BLUEPRINT.post("/upload_file/<scheduled_task_id>")
def upload_scheduled_task_file(scheduled_task_id):
    try:
        project_file = request.files.get('project_file')
        plan_file = request.files.get('plan_file')
        restart_file = request.files.get('restart_file')

        if not any([project_file, plan_file, restart_file]):
            raise Exception("You must select at least one file to edit")

        project_path, plan_path, restart_file_path = schedule_task_service.update_files(
            scheduled_task_id,
            project_file,
            plan_file,
            restart_file
        )

        path = []
        if project_path != None: path.append(project_path)
        if plan_path != None: path.append(plan_path)
        if restart_file_path != None: path.append(restart_file_path)

        return jsonify({'message': 'File uploaded successfully', 'file_path': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@SCHEDULE_API_BLUEPRINT.post("/")
def create_scheduled_task():
    try:
        body = request.get_json()
        required_fields = [
            "frequency", "calibration_id", "calibration_id_for_simulations", "enabled",
            "name", "description", "geometry_id", "start_datetime", "start_condition_type",
            "observation_days", "forecast_days", "border_conditions", "project_file", "plan_file"
        ]
        missing_fields = validate_fields(body, required_fields)
        enabled = body.get("enabled")
        if missing_fields and (enabled is True):
            return jsonify(
                {"error": "Missing required fields for enabled scheduled task", "missing": missing_fields}), 400
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
            "border_conditions": retrieve_series_json(body.get("series_list_file"), body.get("border_conditions")),
            "plan_series_list": retrieve_plan_series_json(body.get("plan_series_file"), body.get("plan_series_list")),
        }

        if params["border_conditions"]:
            if not params['observation_days'] and not params['forecast_days'] and not params['calibration_id']:
                return send_bad_request("observation_days forcast_days and calibration_id must be set")

            exists_forecast_and_observation_values = forecast_and_observation_values_exists_json(
                params["border_conditions"], params["observation_days"], params["forecast_days"],
                params["calibration_id"])

            if not exists_forecast_and_observation_values:
                return send_bad_request("The scheduled task could not be created due to the absence of a boundary "
                                        "series in the INA database for the ID " + str(params["calibration_id"]))

        duplicate_output_series, duplicate_key = check_duplicate_output_series_json(params["plan_series_list"])

        if duplicate_output_series:
            return send_bad_request('The output series (' + duplicate_key[0] + ', ' + duplicate_key[1] + ', ' +
                                    duplicate_key[2] + ') is duplicated. The scheduled task run can not be created.')

        if body.get("start_condition_type") == "initial_flows":
            if not params["initial_flows"]:
                return send_bad_request("intial_flows must be set")
            params["initial_flows"] = create_initial_flows_from_json(body.get("start_condition_type"),
                                                                     body.get("initial_flow_file"),
                                                                     body.get("initial_flow_list"))
        start_condition_type = body.get("start_condition_type")
        restart_file_data = None if body.get("restart_file") is None else file_storage_service.get_file(
            body.get("restart_file"))
        project_file_data = file_storage_service.get_file(body.get("project_file"))
        plan_file_data = file_storage_service.get_file(body.get("plan_file"))

        scheduled_task = schedule_task_service.create(params, start_condition_type, restart_file_data,
                                                      project_file_data, plan_file_data)
        return jsonify({"message": "Success at creating scheduled task",
                        "id": scheduled_task.id})

    except Exception as e:
        logger = get_logger()
        logger.error(e, exc_info=True)
        response = jsonify({
            "message": "bad request while creating scheduled task",
            "error": str(e)
        })
        response.status_code = 400
        return response


@SCHEDULE_API_BLUEPRINT.post("/copy")
def copy_schedule_task():
    try:
        copy_from_id = request.args.get('copyFrom', '')
        if copy_from_id is None:
            return jsonify({"error": "copyFrom parameter not specified"}), 400
        schedule_task = schedule_task_service.copy_schedule_task(copy_from_id)
        response = jsonify({"message": "Scheduled task with id " + copy_from_id + " copied successfully",
                            "id": schedule_task.id})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({"message": "error copying geometry " + copy_from_id,
                            "error": str(e)})
        response.status_code = 400
        return response


def send_bad_request(message):
    response = jsonify({"message": message})
    response.status_code = 400
    return response
