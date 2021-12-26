from flask import Blueprint, render_template

from src.service import geometry_service, execution_plan_service
from src.view.forms.execution_plan_form import ExecutionPlanForm
from src.view.forms.geometry_form import GeometryForm

VIEW_BLUEPRINT = Blueprint("view_controller", __name__)


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

    geometry_data = {
        "id": geometry.id,
        "description": geometry.description,
        "user_fullname": geometry.user.fullname,
        "file_url": geometry_url,
        "file_name": geometry.name,
        "created_at": geometry.created_at.strftime("%d/%m/%Y"),
    }

    return render_template(
        "geometry.html",
        form=GeometryForm(),
        readonly=True,
        errors=errors,
        **geometry_data,
    )


@VIEW_BLUEPRINT.route("/geometry/list")
def geometry_list():
    return render_template("geometry_list.html")


@VIEW_BLUEPRINT.route("/geometry/new")
def geometry_new():
    return render_template("geometry.html", form=GeometryForm())


@VIEW_BLUEPRINT.route("/execution_plan/<execution_plan_id>")
def execution_plan_read(execution_plan_id):
    execution_plan = execution_plan_service.get_execution_plan(execution_plan_id)
    errors = []
    geometry_url = execution_plan.get_geometry_file_url()
    if not geometry_url:
        errors.append(f"Error obteniendo archivo de geometría. Intente nuevamente")
    flow_url = execution_plan.get_flow_file_url()
    if not flow_url:
        errors.append(
            f"Error obteniendo archivo de condiciones de borde. Intente nuevamente"
        )

    user = execution_plan.user

    execution_plan_data = {
        "id": execution_plan.id,
        "plan_name": execution_plan.plan_name,
        "geometry_file_name": geometry_url,
        "flow_file_url": flow_url,
        "user_fullname": user.fullname,
        "start_date": execution_plan.start_datetime.date(),
        "end_date": execution_plan.end_datetime.date(),
        "created_at": execution_plan.created_at.date(),
    }

    return render_template(
        "execution_plan.html",
        form=ExecutionPlanForm(),
        readonly=True,
        errors=errors,
        **execution_plan_data,
    )


@VIEW_BLUEPRINT.route("/execution_plan/list")
def execution_plan_list():
    return render_template("execution_plan_list.html")


@VIEW_BLUEPRINT.route("/execution_plan/new")
def execution_plan_new():
    geometries = geometry_service.get_geometries()
    data = {"form": ExecutionPlanForm(), "geometries": geometries}
    return render_template("execution_plan.html", **data)
