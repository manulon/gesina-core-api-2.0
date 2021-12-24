from flask import Blueprint, render_template

from src.service import geometry_service
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
    if not geometry.get_file_url():
        errors.append(
            f"Error obteniendo archivo de geometría {geometry.name}. Intente nuevamente"
        )

    geometry_data = {
        "id": geometry.id,
        "description": geometry.description,
        "user_fullname": geometry.user.fullname,
        "file_url": geometry.get_file_url(),
        "file_name": geometry.name,
        "created_at": geometry.created_at.date(),
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
    return render_template("execution_plan.html")


@VIEW_BLUEPRINT.route("/execution_plan/list")
def execution_plan_list():
    return render_template("execution_plan_list.html")


@VIEW_BLUEPRINT.route("/execution_plan/new")
def execution_plan_new():
    geometries = geometry_service.get_geometries()
    data = {"form": ExecutionPlanForm(), "geometries": geometries}
    return render_template("execution_plan.html", **data)
