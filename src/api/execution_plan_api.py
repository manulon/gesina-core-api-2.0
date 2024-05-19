from flask import request, jsonify, Blueprint

from src import logger
from src.api.utils import validate_fields
from src.logger import get_logger
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service import (
    execution_plan_service,
    file_storage_service,
    api_authentication_service
)
from src.service.file_storage_service import FileType, get_files_for_id

EXECUTION_PLAN_API_BLUEPRINT = Blueprint("execution_plan", __name__, url_prefix="/execution_plan")


@EXECUTION_PLAN_API_BLUEPRINT.get("/<execution_plan_id>")
def get_execution_plan(execution_plan_id):
    try:
        execution_plan = execution_plan_service.get_execution_plan(execution_plan_id)
        if execution_plan is None:
            raise Exception(f'Execution plan {execution_plan_id} does not exist')
        execution_plan_dict = execution_plan.to_dict()

        result_files = [
            f.object_name
            for f in file_storage_service.list_execution_files(
                FileType.RESULT, execution_plan_id
            )
        ]

        execution_plan_dict["files"] = get_files_for_id(FileType.EXECUTION_PLAN,execution_plan_id, request.args.get('full_content', '').lower())
        execution_plan_dict["result_files"] = result_files

        return jsonify(execution_plan_dict)
    except Exception as e:
        get_logger().error(e,exc_info=True)
        response = jsonify({"error while getting execution plan": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.post("/copy")
def copy_execution_plan():
    try:
        copy_from = request.args.get('copyFrom', '')
        execution_plan = execution_plan_service.copy_execution_plan(copy_from)
        return {"new_execution_plan_id": execution_plan.id}
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.post("/")
def create_execution_plan():
    try:
        required_fields = ["plan_name", "geometry_id"]
        body = request.get_json()
        missing_fields = validate_fields(body, required_fields)
        if missing_fields:
            return jsonify(
                {"error": "Missing required fields for execution plan", "missing": missing_fields}), 400
        execution_plan = execution_plan_service.create_from_json(body,
                                                                 api_authentication_service.get_current_user_id())
        return jsonify({"id": execution_plan.id})
    except Exception as e:
        get_logger().error(e,exc_info=True)
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.delete("/<execution_plan_id>")
def delete_execution_plan(execution_plan_id):
    try:
        execution_plan_service.delete_execution_plan(execution_plan_id)
        response = jsonify({"message": "Execution plan with id " + execution_plan_id + " deleted successfully"})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({"message": "error deleting execution plan " + execution_plan_id,
                            "error": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.patch("/<execution_plan_id>")
def edit_execution_plan(execution_plan_id):
    try:
        body = request.get_json()
        plan_name = body.get("plan_name")
        geometry_id = body.get("geometry_id")
        plan_file = body.get("plan_file")
        flow_file = body.get("flow_file")
        restart_file = body.get("restart_file")
        execution_output_list = body.get("execution_output_list")
        project_file = body.get("project_file")
        execution_plan_service.edit_execution_plan(execution_plan_id, plan_name, geometry_id, project_file, plan_file,
                                                   flow_file, restart_file, execution_output_list)
        return jsonify({"message": f"successfully edited execution plan with id: {execution_plan_id}"})
    except Exception as e:
        response = jsonify({"message": "error deleting editing plan " + execution_plan_id,
                            "error": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.post("/upload_file/<execution_plan_id>")
def upload_execution_file(execution_plan_id):
    try:
        file = request.files['file']
        if file.filename == '':
            raise Exception("No selected file")

        path = file_storage_service.save_file(
            FileType.EXECUTION_PLAN,
            file,
            file.filename,
            execution_plan_id
        )

        return jsonify({'message': 'File uploaded successfully', 'file_path': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@EXECUTION_PLAN_API_BLUEPRINT.get("/plans")
def list_execution_plans():
    try:
        execution_plans = execution_plan_service.get_execution_plans_json(name=request.args.get('plan_name', None),
                                                                          user_last_name=request.args.get(
                                                                              'user_last_name', None),
                                                                          user_first_name=request.args.get(
                                                                              'user_first_name', None),
                                                                          status=request.args.get('status', None),
                                                                          date_from=request.args.get('date_from', None),
                                                                          date_to=request.args.get('date_to', None)
                                                                          )

        return jsonify(execution_plans)
    except Exception as e:
        response = jsonify({"message": "error retrieving execution plans ",
                            "error": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.post("/<execution_id>")
def execute_plan(execution_id):
    from src.tasks import queue_or_fake_simulate

    try:
        queue_or_fake_simulate(execution_id)
        execution_plan_service.update_execution_plan_status(
            execution_id, ExecutionPlanStatus.RUNNING
        )
        return get_execution_plan(execution_id)
    except Exception as e:
        logger.error(e)
        response = jsonify({"message": "error while running execution plan " + execution_id,
                            "error": str(e)})
        response.status_code = 400
        return response
    
@EXECUTION_PLAN_API_BLUEPRINT.post("/cancel/<execution_id>")
def cancel_execution_plan(execution_id):
    from src.tasks import cancel_simulation

    try:
        cancel_simulation(execution_id)
        return get_execution_plan(execution_id)
    except Exception as e:
        logger.error(e)
        response = jsonify({"message": "error while cancelling execution plan " + execution_id,
                            "error": str(e)})
        response.status_code = 400
        return response


@EXECUTION_PLAN_API_BLUEPRINT.get("/files/<execution_plan_id>")
def get_execution_plan_files(execution_plan_id):
    try:
        execution_files = [
            f.object_name
            for f in file_storage_service.list_execution_files(
                FileType.EXECUTION_PLAN, execution_plan_id
            )
        ]
        execution_plan_dict = {}
        execution_plan_dict["execution_files"] = []
        for i in execution_files:
            data = file_storage_service.get_file(i).data
            file = {"name": i.split("/")[-1]}
            execution_plan_dict["execution_files"].append(file)

        return jsonify(execution_plan_dict)
    except Exception as e:
        response = jsonify({"error while getting files for execution plan": str(e)})
        response.status_code = 400
        return response
