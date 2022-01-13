from flask import Blueprint, render_template

from src.view.forms.users_forms import LoginForm, SingUpForm

PUBLIC_VIEW_BLUEPRINT = Blueprint("public_view_controller", __name__)


@PUBLIC_VIEW_BLUEPRINT.route("/login", methods=["GET"])
def login():
    return render_template("login.html", form=LoginForm())


@PUBLIC_VIEW_BLUEPRINT.route("/sign-up", methods=["GET"])
def sign_up():
    return render_template("sign_up.html", form=SingUpForm())
