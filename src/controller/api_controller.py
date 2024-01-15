import json

import sqlalchemy
from flask import Blueprint, request, jsonify

from src import logger
from src.controller.schemas import ActivityParams
import traceback
import io
from src.login_manager import user_is_authenticated
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service import (
    geometry_service,
    execution_plan_service,
    user_service,
    file_storage_service,

)
from src.service.exception.activity_exception import ActivityException
from src.service.exception.file_exception import FileUploadError
from src.service.exception.series_exception import SeriesUploadError
from src.service.file_storage_service import FileType
from src.service.ina_service import validate_connection_to_service
from src.view.forms.execution_plan_form import ExecutionPlanForm
from src.view.forms.geometry_form import GeometryForm
from src.view.forms.schedule_config_form import (
    ScheduleConfigForm,
    InitialFlowForm,
    SeriesForm,
    IntervalForm,
    PlanSeriesForm,
)
from src.view.forms.users_forms import EditUserForm
from src.service.api_authentication_service import before_api_request

API_BLUEPRINT = Blueprint("api_controller", __name__)
API_BLUEPRINT.before_request(before_api_request)


@API_BLUEPRINT.get("/")
def home():
    return {"status": "ok"}



@API_BLUEPRINT.get("/execution_plan/<execution_plan_id>")
def get_execution_plan(execution_plan_id):
    execution_plan = execution_plan_service.get_execution_plan(execution_plan_id)
    execution_plan_dict = execution_plan.to_dict()
    execution_files = [
        f.object_name
        for f in file_storage_service.list_execution_files(
            FileType.EXECUTION_PLAN, execution_plan_id
        )
    ]
    full_content_param = request.args.get('full_content', '').lower() == 'true'
    if full_content_param:
        execution_plan_dict["files"] = []
        for i in execution_files:
            data = file_storage_service.get_file(i).data
            file = {"name": i.split("/")[-1], "content": str(data)}
            execution_plan_dict["files"].append(file)
    else:
        execution_plan_dict["files"] = [i.split("/")[-1] for i in execution_files]

    return jsonify(execution_plan_dict)


@API_BLUEPRINT.post("/execution_plan/copy")
def copy_execution_plan():
    try:
        copy_from = request.args.get('copyFrom', '')
        execution_plan = execution_plan_service.copy_execution_plan(copy_from)
        return {"new_execution_plan_id": execution_plan.id}
    except Exception as e:
        print(e.with_traceback())
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response


@API_BLUEPRINT.post("/execution_plan")
def create_execution_plan():
    try:
        execution_plan = execution_plan_service.create_from_json(request.get_json())
        return {"new_execution_plan_id": execution_plan.id}
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 400
        return response


@API_BLUEPRINT.delete("execution_plan/<execution_plan_id>")
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
    
@API_BLUEPRINT.patch("execution_plan/edit/<execution_plan_id>")
def edit_execution_plan(execution_plan_id):
    try:
        body = request.get_json()
        plan_name = body.get("plan_name")
        geometry_id = body.get("geometry_id")
        plan_file = body.get("plan_file")
        flow_file = body.get("flow_file")
        restart_file = body.get("restart_file")
        execution_plan_output = body.get("execution_output_list")
        project_file = body.get("project_file")    
        execution_plan_service.edit_execution_plan(execution_plan_id,plan_name,geometry_id,project_file,plan_file,flow_file,restart_file, execution_plan_output)
        return jsonify({"message":f"successfully edited execution plan with id: {execution_plan_id}"})
    except Exception as e:
        response = jsonify({"message": "error deleting editing plan " + execution_plan_id,
                            "error": str(e)})
        response.status_code = 400
        return response
    

@API_BLUEPRINT.post("execution_plan/upload_file")
def upload_execution_file():
    try:
        body = request.get_json()
        data = body.get("data")
        execution_plan_id = body.get("execution_plan_id")
        file_name = body.get("file_name")
        if file_name is None or data is None:
            raise Exception("file_name and data must have a value")
        path = file_storage_service.save_file(FileType.EXECUTION_PLAN, io.BytesIO(bytes(data, encoding="utf-8")), file_name,execution_plan_id)
        return jsonify({"message": f"success at uploading file at path {path}"})
    except Exception as e:
        response = jsonify({"message": "error uploading file ",
                                    "error": str(e)})
        response.status_code = 400
        return response
    

@API_BLUEPRINT.get("/execution_plans")
def list_execution_plans():
    try:
        execution_plans = execution_plan_service.get_execution_plans_json(name=request.args.get('plan_name', None), 
                                                                        user_last_name=request.args.get('user_last_name', None),
                                                                        user_first_name=request.args.get('user_first_name', None),
                                                                        status=request.args.get('status', None),
                                                                        date_from=request.args.get('date_from', None),
                                                                        date_to=request.args.get('date_to',None)
                                                                        )
        
        return jsonify(execution_plans)
    except Exception as e:
        response = jsonify({"message": "error retrieving execution plans ",
                                    "error": str(e)})
        response.status_code = 400
        return response
    

@API_BLUEPRINT.post("/execution_plan/<execution_id>")
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
        response = jsonify({"message": "error while running execution plan " + execution_id ,
                                    "error": str(e)})
        response.status_code = 400
        return response
        

    

        
