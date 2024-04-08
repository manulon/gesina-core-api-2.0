import sqlalchemy
from flask import Blueprint, render_template, url_for, redirect, request, jsonify

import requests
from src import logger, config
from src.controller.schemas import ActivityParams
from src.login_manager import user_is_authenticated
from src.service import (
    geometry_service,
    execution_plan_service,
    user_service,
    file_storage_service,
    schedule_task_service,
    notification_service,
    activity_service,
)
from src.service.exception.activity_exception import ActivityException
from src.service.exception.file_exception import FileUploadError
from src.service.exception.series_exception import SeriesUploadError
from src.service.border_series_service import retrieve_series
from src.service.file_storage_service import FileType, save_file
from src.service.ina_service import validate_connection_to_service
from src.view.forms.execution_plan_form import ExecutionPlanForm, EditedExecutionPlanForm
from src.view.forms.geometry_form import GeometryForm
from src.view.forms.schedule_config_form import (
    ScheduleConfigForm,
    InitialFlowForm,
    SeriesForm,
    IntervalForm,
    PlanSeriesForm,
)
from src.view.forms.users_forms import EditUserForm
from pytz import utc, timezone
from datetime import datetime
from datetime import timedelta


VIEW_BLUEPRINT = Blueprint("view_controller", __name__)
VIEW_BLUEPRINT.before_request(user_is_authenticated)


@VIEW_BLUEPRINT.route("/")
def home():
    activity_params = ActivityParams().load(request.args)
    try:
        (
            execution_results,
            execution_time_average,
            contributions,
        ) = activity_service.get_activity(activity_params)
        return render_template(
            "dashboard.html",
            execution_results=execution_results,
            execution_time_average=execution_time_average,
            contributions=contributions,
            refresh_rate=activity_params.get("refresh_rate"),
            date_from=activity_params.get("date_from"),
            date_to=activity_params.get("date_to"),
        )
    except ActivityException as activity_exception:
        logger.error(activity_exception)
        error_message = activity_exception.message

        return render_template(
            "dashboard.html",
            execution_results=None,
            execution_time_average=None,
            refresh_rate=-1,
            errors=[error_message],
        )
    except Exception as generic_exception:
        logger.error(generic_exception)
        error_message = "Hubo un error inesperado. Intente nuevamente."

        return render_template(
            "dashboard.html",
            execution_results=None,
            execution_time_average=None,
            refresh_rate=-1,
            errors=[error_message],
        )


@VIEW_BLUEPRINT.route("/user")
def user_list():
    user = user_service.get_current_user()
    if user.admin_role:
        return render_template("user_list.html")
    else:
        return redirect(
            url_for(
                "view_controller.home",
            )
        )


@VIEW_BLUEPRINT.route("/user/<user_id>")
def edit_user(user_id):
    if user_service.get_current_user().admin_role:
        user = user_service.get_user(user_id)
        return render_template(
            "user_login_sign-up.html",
            form=EditUserForm(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                admin_role=user.admin_role,
                user_id=user.id,
            ),
        )
    else:
        return redirect(
            url_for(
                "view_controller.home",
            )
        )


@VIEW_BLUEPRINT.route("/geometry/<geometry_id>")
def geometry_read(geometry_id):
    geometry = geometry_service.get_geometry(geometry_id)
    errors = []

    return render_template(
        "geometry.html",
        form=GeometryForm(),
        readonly=True,
        errors=errors,
        geometry=geometry,
    )


@VIEW_BLUEPRINT.route("/geometry/list")
def geometry_list():    
    delete_success = request.args.get('delete_success')
    delete_failed = request.args.get('delete_failed')
    geometry_in_use = request.args.get('geometry_in_use')
    edit_success = request.args.get('edit_success')
    edit_failed = request.args.get('edit_failed')

    message = None

    if delete_success:
        message = "La geometría #" + delete_success +  " ha sido eliminado con éxito."
        return render_template("geometry_list.html", success_message=message)
    
    if delete_failed:
        message = "Ha ocurrido un error al eliminar la geometría #" + delete_failed
        return render_template("geometry_list.html", errors=[message])
    
    if geometry_in_use:
        message = "Ha ocurrido un error al eliminar la geometría #" + geometry_in_use + ". Esta está siendo usada en un plan de ejecución activo."
        return render_template("geometry_list.html", errors=[message])
    
    if edit_success:
        message = "La geometría #" + edit_success +  " ha sido editada con éxito."
        return render_template("geometry_list.html", success_message=message)
    
    if edit_failed:
        message = "Ha ocurrido un error al editar la geometría #" + edit_failed
        return render_template("geometry_list.html", errors=[message])

    return render_template("geometry_list.html")    

@VIEW_BLUEPRINT.route("/geometry")
def geometry_new():
    return render_template("geometry.html", form=GeometryForm())

@VIEW_BLUEPRINT.route("/geometry", methods=["POST"])
def save_geometry():
    form = GeometryForm()
    user = user_service.get_current_user()
    try:
        if form.validate_on_submit():
            geometry = geometry_service.create(
                form.file.data.filename,
                form.file.data,
                form.description.data,
                user
            )
            success_message = f"Geometría #{str(geometry.id)} creada con éxito."
            return render_template(
                "geometry_list.html", success_message=success_message
            )

        return render_template("geometry.html", form=form, errors=form.get_errors())
    except sqlalchemy.exc.IntegrityError as database_error:
        logger.error(database_error)
        error_message = "Error guardando información en la base de datos."

        return render_template("geometry.html", form=form, errors=[error_message])
    except FileUploadError as file_error:
        logger.error(file_error.message)
        error_message = "Error cargando archivo. Intente nuevamente."

        return render_template("geometry.html", form=form, errors=[error_message])

@VIEW_BLUEPRINT.route("/execution_plan/<execution_plan_id>")
def execution_plan_read(execution_plan_id):
    execution_plan = execution_plan_service.get_execution_plan(execution_plan_id)
    return render_template(
        "execution_plan.html",
        form=ExecutionPlanForm(),
        readonly=True,
        execution_plan=execution_plan,
        current_user=user_service.get_updated_user(),
        execution_files=[
            f.object_name.split("/")[-1]
            for f in file_storage_service.list_execution_files(
                FileType.EXECUTION_PLAN, execution_plan_id
            )
        ],
        execution_result_files=[
            f.object_name.split("/")[-1]
            for f in file_storage_service.list_execution_files(
                FileType.RESULT, execution_plan_id
            )
        ],
    )


@VIEW_BLUEPRINT.route("read_notification/<notification_id>")
def read_notification(notification_id):
    notification = notification_service.mark_notification_as_read(notification_id)
    return execution_plan_read(notification.execution_plan_id)


@VIEW_BLUEPRINT.route("/notifications/all", methods=["PUT"])
def read_all_notifications_for_user():
    user = user_service.get_current_user()
    notification_service.read_all_user_notifications(user.id)
    return {"result": "OK"}, 201

@VIEW_BLUEPRINT.route('/execution_plan/list/')
def execution_plan_list():
    cancel_success = request.args.get('cancel_success')
    delete_success = request.args.get('delete_success')
    delete_failed = request.args.get('delete_failed')
    duplicate_success = request.args.get('duplicate_success')
    duplicate_failed = request.args.get('duplicate_failed')

    message = None
    
    if cancel_success:
        message = "El plan de ejecucion #" + cancel_success +  " ha sido cancelado con éxito."
        return render_template("execution_plan_list.html", success_message=message)

    if delete_success:
        message = "El plan de ejecucion #" + delete_success +  " ha sido eliminado con éxito."
        return render_template("execution_plan_list.html", success_message=message)
    
    if delete_failed:
        message = "Ha ocurrido un error al eliminar el plan de ejecucion #" + delete_failed
        return render_template("execution_plan_list.html", errors=[message])
    
    if duplicate_success:
        message = "El plan de ejecucion #" + duplicate_success +  " ha sido duplicado con éxito."
        return render_template("execution_plan_list.html", success_message=message)
    
    if duplicate_failed:
        message = "Ha ocurrido un error al duplicar el plan de ejecucion #" + duplicate_failed
        return render_template("execution_plan_list.html", errors=[message])

    return render_template("execution_plan_list.html")        
    
@VIEW_BLUEPRINT.route("/execution_plan")
def execution_plan_new():
    geometries = geometry_service.get_geometries()
    data = {"form": ExecutionPlanForm(), "geometries": geometries}
    return render_template("execution_plan.html", **data)

@VIEW_BLUEPRINT.route("/execution_plan", methods=["POST"])
def save_execution_plan():
    form = ExecutionPlanForm()
    try:
        if form.validate_on_submit():
            execution_plan = execution_plan_service.create_from_form(form)
            success_message = f"Simulación #{str(execution_plan.id)} creada con éxito."
            return render_template(
                "execution_plan_list.html", success_message=success_message
            )

        return render_template(
            "execution_plan.html", form=form, errors=form.get_errors()
        )
    except sqlalchemy.exc.IntegrityError as database_error:
        logger.error(database_error)
        error_message = "Error guardando información en la base de datos."

        return render_template("execution_plan.html", form=form, errors=[error_message])
    except FileUploadError as file_error:
        logger.error(file_error.message, file_error)
        error_message = "Error cargando archivo. Intente nuevamente."

        return render_template("execution_plan.html", form=form, errors=[error_message])

@VIEW_BLUEPRINT.route("/schedule_tasks/<schedule_task_id>", methods=["GET"])
def get_schedule_task_config(schedule_task_id):
    schedule_config = schedule_task_service.get_schedule_task_config(schedule_task_id)
    return render_schedule_view(ScheduleConfigForm(), schedule_config)


@VIEW_BLUEPRINT.route("/schedule_tasks")
def get_schedule_tasks():
    success_message = request.args.get("success_message", None)
    delete_success = request.args.get('delete_success')
    delete_failed = request.args.get('delete_failed')
    copy_success = request.args.get('copy_success')
    copy_failed = request.args.get('copy_failed')

    message = None

    if delete_success:
        message = "La corrida programada #" + delete_success +  " ha sido eliminada con éxito."
        return render_template("schedule_tasks_list.html", success_message=message)
    
    if delete_failed:
        message = "Ha ocurrido un error al eliminar la corrida programada #" + delete_failed + "."
        return render_template("schedule_tasks_list.html", errors=[message])
    
    if copy_success:
        message = "La corrida programada #" + copy_success +  " ha sido duplicada con éxito."
        return render_template("schedule_tasks_list.html", success_message=message)
    
    if copy_failed:
        message = "Ha ocurrido un error al duplicar la corrida programada #" + copy_failed + "."
        return render_template("schedule_tasks_list.html", errors=[message])
    
    if success_message:
        message = success_message

    return render_template("schedule_tasks_list.html", success_message=message)


@VIEW_BLUEPRINT.route("/schedule_tasks/<schedule_config_id>", methods=["POST"])

@VIEW_BLUEPRINT.route(
    "/schedule_tasks/", methods=["POST"], defaults={"schedule_config_id": None}
)
def save_or_create_schedule_config(schedule_config_id):
    schedule_config = schedule_task_service.get_schedule_task_config(schedule_config_id)
    form = ScheduleConfigForm()

    exists_forecast_and_observation_values, border_conditions = forecast_and_observation_values_exists(form)

    if not exists_forecast_and_observation_values:
        error_message = 'No se pudo crear la ejecucion programada debido a que no se encontró una serie de borde en la base de datos del INA para el ID ' + str(form.calibration_id.data)
        return render_schedule_view(form, schedule_config, [error_message])
    
    try:
        if form.validate_on_submit():
                if schedule_config_id:
                    schedule_task_service.update(schedule_config_id, form)
                else:
                    schedule_config = schedule_task_service.create_from_form(form, border_conditions)
                success_message = "Configuración actualizada con éxito."
                return redirect(
                    url_for(
                        "view_controller.get_schedule_tasks",
                        success_message=success_message,
                    )
                )
        return render_schedule_view(form, schedule_config, form.get_errors())
    except (FileUploadError, SeriesUploadError) as exception:
        logger.error(exception.message)
        return render_schedule_view(form, schedule_config, [exception.message])
    except Exception as exception:
        logger.error(exception)
        error_message = "Error actualizando la configuración."
        return render_schedule_view(form, schedule_config, [error_message])

def forecast_and_observation_values_exists(form):
    locale = timezone("America/Argentina/Buenos_Aires")
    today = datetime.now(tz=locale).replace(minute=0)
    start_date = today - timedelta(form.observation_days.data)
    end_date = today + timedelta(form.forecast_days.data)

    format_time = lambda d: d.strftime("%Y-%m-%d")
    timestart = start_date - timedelta(1)
    timeend = end_date + timedelta(1)

    border_conditions = retrieve_series(form)

    if len(border_conditions) > 0:
        url = f"{config.ina_url}/sim/calibrados/{form.calibration_id.data}/corridas/last?series_id={border_conditions[0].series_id}&timestart={format_time(timestart)}&timeend={format_time(timeend)}"

        response = None
        for i in range(config.max_retries):
            response = requests.get(
                url, headers={"Authorization": f"Bearer {config.ina_token}"}
            )
            if response.status_code == 200 and len(response.json()["series"]) > 0:
                return True, border_conditions
            else:
                return False, None
    else:
        empty_list = []
        return True, empty_list
     
    return False, None

@VIEW_BLUEPRINT.route("/schedule_tasks/validate_border_conditions", methods=["POST"])
def validate_connection_to_schedule_conditions():
    body = request.get_json()
    validation_result = validate_connection_to_service(
        body["calibration_id"], body["series_id"]
    )
    if validation_result:
        return (
            jsonify(
                {
                    "result": f"Se logró correctamente la conexión a la Api del INA para el id de serie {body['series_id']} y id de calibrado {body['calibration_id']}"
                }
            ),
            200,
        )
    return (
        jsonify(
            {
                "result": f"No se logró la conexión a la Api del INA para el id de serie {body['series_id']} y id de calibrado {body['calibration_id']}"
            }
        ),
        200,
    )


@VIEW_BLUEPRINT.route("/schedule_tasks/new", methods=["GET"])
def schedule_task_new():
    return render_schedule_view(ScheduleConfigForm())


@VIEW_BLUEPRINT.route("/execution_plan_edit/<execution_plan_id>")
def execution_plan_edit_view(execution_plan_id):
    geometries = geometry_service.get_geometries()
    data = {"form": EditedExecutionPlanForm(), "execution_plan_id": execution_plan_id,
            "geometries": geometries}
    return render_template("edit_execution_plan.html", **data)


def render_schedule_view(form, schedule_config=None, errors=()):
    _id = None
    form.project_file_present = False
    form.plan_file_present = False
    form.restart_file_present = False
    if schedule_config:
        initial_flows = schedule_config.initial_flows
        border_conditions = schedule_config.border_conditions
        plan_series_list = schedule_config.plan_series_list

        form.project_file_present = schedule_config.is_project_template_present()
        form.plan_file_present = schedule_config.is_plan_template_present()
        form.restart_file_present = schedule_config.is_restart_file_present()
        form.enabled.data = schedule_config.enabled
        form.frequency.data = schedule_config.frequency
        form.calibration_id.data = schedule_config.calibration_id
        form.calibration_id_for_simulations.data = (
            schedule_config.calibration_id_for_simulations
        )
        form.description.data = schedule_config.description
        form.name.data = schedule_config.name
        form.start_datetime.data = schedule_config.start_datetime
        form.geometry_id.process_data(schedule_config.geometry_id)
        form.start_condition_type.process_data(schedule_config.start_condition_type)
        form.observation_days.data = schedule_config.observation_days
        form.forecast_days.data = schedule_config.forecast_days
        render_initial_flows(form, initial_flows)
        render_border_condition(border_conditions, form)
        render_plan_series_list(plan_series_list, form)

        _id = schedule_config.id
        form.idx = schedule_config.id

    return render_template("schedule_config.html", form=form, errors=errors, id=_id)


def render_initial_flows(form, initial_flows):
    clean_form_list(form.initial_flow_list)

    for each_initial_flow in initial_flows:
        initial_flow_form = InitialFlowForm()
        initial_flow_form.river = each_initial_flow.river
        initial_flow_form.reach = each_initial_flow.reach
        initial_flow_form.river_stat = each_initial_flow.river_stat
        initial_flow_form.flow = each_initial_flow.flow
        form.initial_flow_list.append_entry(initial_flow_form)


def render_border_condition(border_condition, form):
    clean_form_list(form.series_list)

    for each_border_condition in border_condition:
        series_form = SeriesForm()
        series_form.river = each_border_condition.river
        series_form.reach = each_border_condition.reach
        series_form.river_stat = each_border_condition.river_stat
        series_form.border_condition = each_border_condition.type
        interval_form = IntervalForm()
        chunks = each_border_condition.interval.split("-")
        interval_form.interval_value = chunks[0]
        interval_form.interval_unit = chunks[1]
        series_form.interval = interval_form
        series_form.series_id = each_border_condition.series_id
        form.series_list.append_entry(series_form)


def render_plan_series_list(plan_series_list, form):
    clean_form_list(form.plan_series_list)

    for plan in plan_series_list:
        plan_form = PlanSeriesForm()
        plan_form.idx = plan.id
        plan_form.reach = plan.reach
        plan_form.river = plan.river
        plan_form.river_stat = plan.river_stat
        plan_form.stage_series_id = plan.stage_series_id
        plan_form.flow_series_id = plan.flow_series_id
        plan_form.stage_datum = plan.stage_datum
        form.plan_series_list.append_entry(plan_form)

def clean_form_list(form_list):
    if form_list:
        for i in range(0, len(form_list)):
            form_list.entries.pop(0)

@VIEW_BLUEPRINT.route("/execution_plan/edit/<execution_plan_id>", methods=["POST"])
def edit_execution_plan(execution_plan_id):
    form = EditedExecutionPlanForm()

    output_list = _get_output_list(form)

    try:
        if form.validate_on_submit():
            
            geometry_to_upload = None
            project_file_to_upload = None
            plan_file_to_upload = None
            flow_file_to_upload = None
            restart_file_to_upload = None

            if form.geometry_option.data != "default":
                geometry_to_upload = int(form.geometry_option.data)

            if form.project_file.data != None:
                project_file_to_upload = save_file(FileType.EXECUTION_PLAN, form.project_file.data, 
                                                   form.project_file.data.filename)
                
                
            if form.plan_file.data != None:
                plan_file_to_upload = save_file(FileType.EXECUTION_PLAN, form.plan_file.data, 
                                                form.plan_file.data.filename)
                
            if form.flow_file.data != None:
                flow_file_to_upload = save_file(FileType.EXECUTION_PLAN, form.flow_file.data, 
                                                form.flow_file.data.filename)
                
            if form.restart_file.data != None:
                restart_file_to_upload = save_file(FileType.EXECUTION_PLAN, form.restart_file.data, 
                                                    form.restart_file.data.filename)

            # No estoy pasando el execution plan output
            execution_plan = execution_plan_service.edit_execution_plan(execution_plan_id, 
                                                                        geometry_id = geometry_to_upload,
                                                                        plan_name = form.plan_name.data,
                                                                        project_file = project_file_to_upload,
                                                                        plan_file = plan_file_to_upload,
                                                                        flow_file = flow_file_to_upload,
                                                                        restart_file = restart_file_to_upload,
                                                                        execution_plan_output = output_list)
            
            success_message = f"Simulación #{str(execution_plan.id)} editada con éxito."
            return render_template(
                "execution_plan_list.html", success_message=success_message
            )

    except sqlalchemy.exc.IntegrityError as database_error:
        logger.error(database_error)
        error_message = "Error guardando información en la base de datos."

        return render_template("execution_plan.html", form=form, errors=[error_message])
    
    except FileUploadError as file_error:
        logger.error(file_error.message, file_error)
        error_message = "Error cargando archivo. Intente nuevamente."

        return render_template("execution_plan.html", form=form, errors=[error_message])
    
def _get_output_list(form):
    execution_plan_output_list = []

    river = request.form.getlist(f'execution_plan_output_list-0-river')
    reach = request.form.getlist(f'execution_plan_output_list-0-reach')
    river_stat = request.form.getlist(f'execution_plan_output_list-0-river_stat')

    for i in range(len(river)):
        execution_plan_output_list.append({"river": river[i], 
                                           "reach": reach[i], 
                                           "river_stat": river_stat[i]})

    return execution_plan_output_list

@VIEW_BLUEPRINT.route("/geometry_edit/<geometry_id>")
def geometry_edit_view(geometry_id):
    geometry = geometry_service.get_geometry(geometry_id)
    data = {"geometry": geometry}
    return render_template("edit_geometry.html", **data)