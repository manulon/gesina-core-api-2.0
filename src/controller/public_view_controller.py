import flask
from flask import Blueprint, render_template, url_for
from flask_login import login_user

from src.service import user_service
from src.view.forms.users_forms import LoginForm, SingUpForm

PUBLIC_VIEW_BLUEPRINT = Blueprint("public_view_controller", __name__)


@PUBLIC_VIEW_BLUEPRINT.route("/login", methods=["GET"])
def login():
    return render_template("user_login_sign-up.html", form=LoginForm())


@PUBLIC_VIEW_BLUEPRINT.route("/sign-up", methods=["GET"])
def sign_up():
    return render_template("user_login_sign-up.html", form=SingUpForm())


@PUBLIC_VIEW_BLUEPRINT.route("/sign-up", methods=["POST"])
def do_sign_up():
    form = SingUpForm()
    if form.validate_on_submit():
        user_service.save(
            form.email.data,
            form.first_name.data,
            form.last_name.data,
            form.password.data,
        )
        return flask.redirect(url_for("public_view_controller.login"))
    return render_template(
        "user_login_sign-up.html", form=form, errors=form.get_errors()
    )


@PUBLIC_VIEW_BLUEPRINT.route("/login", methods=["POST"])
def do_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = user_service.get_user_by_email_and_password(
            form.email.data, form.password.data
        )

        if user:
            next = flask.request.args.get("next")
            login_user(user)
            flask.flash("Logged in successfully.")

            return flask.redirect(
                next or flask.url_for("view_controller.execution_plan_list")
            )
        else:
            return render_template(
                "user_login_sign-up.html",
                form=form,
                errors=["Usuario/contraseña inválido"],
            )

    return render_template(
        "user_login_sign-up.html", form=form, errors=form.get_errors()
    )
