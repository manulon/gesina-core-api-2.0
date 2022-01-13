import flask
from flask import Blueprint, url_for
import flask_login
from flask_login import login_user, login_required

from src.service import user_service
from src.view.forms.users_forms import SingUpForm, LoginForm

USER_BLUEPRINT = Blueprint("user_controller", __name__)


@USER_BLUEPRINT.route("/logout", methods=["GET"])
@login_required
def do_logout():
    flask_login.logout_user()
    return flask.redirect(url_for("public_view_controller.login"))


@USER_BLUEPRINT.route("/sign-up", methods=["POST"])
def do_sign_up():
    form = SingUpForm()
    if form.validate():
        data = form.data
        data.pop("csrf_token")
        user_service.save(**data)
    return flask.redirect(url_for("public_view_controller.login"))


@USER_BLUEPRINT.route("/login", methods=["POST"])
def do_login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        data.pop("csrf_token")
        user = user_service.get_user_by_email_and_password(**data)

        if user:
            next = flask.request.args.get("next")
            login_user(user)
            flask.flash("Logged in successfully.")

            return flask.redirect(
                next or flask.url_for("view_controller.execution_plan_list")
            )
