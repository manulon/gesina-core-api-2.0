import flask_login
import sqlalchemy
from flask import Blueprint, render_template, url_for, redirect

from src import logger
from src.login_manager import user_is_authenticated
from src.service import (
    geometry_service,
    execution_plan_service,
    user_service,
    file_storage_service,
    schedule_task_service,
    notification_service,
)
from src.service.exception.file_exception import FileUploadError
from src.service.file_storage_service import FileType
from src.view.forms.execution_plan_form import ExecutionPlanForm
from src.view.forms.geometry_form import GeometryForm
from src.view.forms.schedule_config_form import ScheduleConfigForm

VIEW_BLUEPRINT = Blueprint("view_controller", __name__)
VIEW_BLUEPRINT.before_request(user_is_authenticated)

VIEW_BLUEPRINT.before_request(user_is_authenticated)


@VIEW_BLUEPRINT.route("/")
def home():
    return render_template("execution_plan_list.html")


@VIEW_BLUEPRINT.route("/geometry/<geometry_id>")
def geometry_read(geometry_id):
    geometry = geometry_service.get_geometry(geometry_id)
    errors = []
    geometry_url = geometry.get_file_url()
    if not geometry_url:
        errors.append(
            f"Error obteniendo archivo de geometría {geometry.name}. Intente nuevamente"
        )

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
            return render_template("geometry_list.html", success=success_message)

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


@VIEW_BLUEPRINT.route("/notifications/all/<user_id>", methods=["PUT"])
def read_all_notifications_for_user(user_id):
    notification_service.read_all_user_notifications(user_id)
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
            return render_template("execution_plan_list.html", success=success_message)

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


@VIEW_BLUEPRINT.route("/schedule_config")
def get_schedule_task_config():
    schedule_config = schedule_task_service.get_schedule_task_config()
    return render_schedule_view(ScheduleConfigForm(), schedule_config, [])


@VIEW_BLUEPRINT.route("/schedule_config/<schedule_config_id>", methods=["POST"])
def save_schedule_config(schedule_config_id):
    schedule_tasks_configs = schedule_task_service.get_schedule_task_config()
    form = ScheduleConfigForm()
    try:
        if form.validate_on_submit():
            schedule_task_service.update(schedule_config_id, form)
            success_message = "Configuración actualizada con éxito."
            return render_template("execution_plan_list.html", success=success_message)

        return render_schedule_view(form, schedule_tasks_configs, form.get_errors())
    except Exception as exception:
        logger.error(exception)
        error_message = "Error actualizando la configuración."

        return render_schedule_view(form, schedule_tasks_configs, [error_message])


def render_schedule_view(form, schedule_config, errors):
    return render_template(
        "schedule_config.html",
        form=form,
        schedule_config=schedule_config,
        errors=errors,
    )


@VIEW_BLUEPRINT.route("/user/logout", methods=["GET"])
def do_logout():
    flask_login.logout_user()
    return redirect(url_for("public_view_controller.login"))
