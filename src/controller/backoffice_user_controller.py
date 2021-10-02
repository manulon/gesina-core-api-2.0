from flask import render_template, Blueprint, request, make_response, redirect, url_for

from src.service import backoffice_user_service

BACKOFFICE_USER_BLUEPRINT = Blueprint("backoffice_user_controller", __name__)


@BACKOFFICE_USER_BLUEPRINT.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@BACKOFFICE_USER_BLUEPRINT.route("/login", methods=["POST"])
def create_session():
    params = {"username": "admin", "password": "admin"}
    session_id = backoffice_user_service.create_session_id(**params)
    if session_id is None:
        return render_template("login.html", incorrect=True)
    response = make_response(redirect(url_for("backoffice_controller.home")))
    response.set_cookie("session_id", str(session_id))
    return response


@BACKOFFICE_USER_BLUEPRINT.route("/logout", methods=["GET"])
def logout():
    session_id = request.cookies.get("session_id")
    backoffice_user_service.clear_session_id(session_id)
    resp = make_response(render_template("login.html"))
    resp.delete_cookie("session_id")
    return resp
