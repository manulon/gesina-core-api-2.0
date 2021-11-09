from flask import Blueprint, render_template
from view.view_error import ViewError


VIEW_BLUEPRINT = Blueprint("view_controller", __name__)


@VIEW_BLUEPRINT.route("/", defaults={"path": ""})
def home():
    return render_template("dashboard.html")


@VIEW_BLUEPRINT.route("/geometry/list")
def geometry_list():
    return render_template("geometry_list.html")


@VIEW_BLUEPRINT.route("/geometry/new")
def geometry_new():
    return render_template("geometry_new.html", error=ViewError("Un error"))


@VIEW_BLUEPRINT.route("/execution_plan/list")
def execution_plan_list():
    return render_template("execution_plan_list.html")


@VIEW_BLUEPRINT.route("/execution_plan/new")
def execution_plan_new():
    return render_template("execution_plan_new.html")
