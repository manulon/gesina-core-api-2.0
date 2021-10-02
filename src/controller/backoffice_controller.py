from flask import Blueprint, render_template, redirect, url_for

from src.service import backoffice_user_service

BACKOFFICE_BLUEPRINT = Blueprint("backoffice_controller", __name__)


def require_login():
    backoffice_user = backoffice_user_service.current_user()
    if backoffice_user is None:
        return redirect(url_for("backoffice_user_controller.login"))


# BACKOFFICE_BLUEPRINT.before_request(require_login)


@BACKOFFICE_BLUEPRINT.route("/")
@BACKOFFICE_BLUEPRINT.route("")
def home():
    return render_template("dashboard.html")


@BACKOFFICE_BLUEPRINT.route("/app_users")
def app_users():
    return render_template("app_users.html", app_users=[])


@BACKOFFICE_BLUEPRINT.route("/app_users/<_id>")
def app_user(_id):
    return render_template("app_user.html", app_user=[])


@BACKOFFICE_BLUEPRINT.route("/complaints")
def complaints():
    return render_template("complaints.html")
