from flask import render_template, Blueprint, make_response, redirect, url_for, jsonify
import flask_login

from src.service import user_service
from src.view.forms.users_forms import SingUpForm
import logging

USER_BLUEPRINT = Blueprint("user_controller", __name__)


@USER_BLUEPRINT.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@USER_BLUEPRINT.route("/logout", methods=["GET"])
def logout():
    flask_login.logout_user()
    return jsonify({"status": "ok"})


@USER_BLUEPRINT.route("/sign-up", methods=["GET"])
def sign_up():
    return render_template("sign_up.html", form=SingUpForm())


@USER_BLUEPRINT.route("/sign-up", methods=["POST"])
def do_sign_up():
    form = SingUpForm()
    if form.validate():
        data = form.data
        data.pop("csrf_token")
        user_service.save(**data)
    return "ok"
