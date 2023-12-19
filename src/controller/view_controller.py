import sqlalchemy
from flask import Blueprint, render_template, url_for, redirect, request, jsonify

from src import logger
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
            geometry = geometry_service.create(form, user)
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


@VIEW_BLUEPRINT.route("/execution_plan/list")
def execution_plan_list():
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
    return render_template("schedule_tasks_list.html", success_message=success_message)


@VIEW_BLUEPRINT.route("/schedule_tasks/<schedule_config_id>", methods=["POST"])
@VIEW_BLUEPRINT.route(
    "/schedule_tasks/", methods=["POST"], defaults={"schedule_config_id": None}
)
def save_or_create_schedule_config(schedule_config_id):
    schedule_config = schedule_task_service.get_schedule_task_config(schedule_config_id)
    form = ScheduleConfigForm()
    try:
        if form.validate_on_submit():
            if schedule_config_id:
                schedule_task_service.update(schedule_config_id, form)
            else:
                schedule_config = schedule_task_service.create(form)

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


@VIEW_BLUEPRINT.route("/execution_plan_derivate")
def edit_execution_plan():
    return render_template("edit_execution_plan.html")


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
        form.plan_series_list.append_entry(plan_form)


def clean_form_list(form_list):
    if form_list:
        for i in range(0, len(form_list)):
            form_list.entries.pop(0)


