from flask import Blueprint, render_template

VIEW_BLUEPRINT = Blueprint("view_controller", __name__)


@VIEW_BLUEPRINT.route("/", defaults={"path": ""})
def home():
    return render_template("dashboard.html")


class Prueba:
    def __init__(self):
        self.description = "description"
        self.id = 1
        self.file_url = "https://www.adslzone.net/app/uploads-adslzone.net/2019/04/borrar-fondo-imagen.jpg"


@VIEW_BLUEPRINT.route("/geometry")
def geometry_read():

    return render_template("geometry_read.html", geometry=Prueba())


@VIEW_BLUEPRINT.route("/geometry/list")
def geometry_list():
    return render_template("geometry_list.html")


@VIEW_BLUEPRINT.route("/geometry/new")
def geometry_new():
    return render_template("geometry_new.html")


@VIEW_BLUEPRINT.route("/execution_plan/list")
def execution_plan_list():
    return render_template("execution_plan_list.html")


@VIEW_BLUEPRINT.route("/execution_plan/new")
def execution_plan_new():
    return render_template("execution_plan_new.html")
