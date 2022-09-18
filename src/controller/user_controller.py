from flask import Blueprint, jsonify, redirect, url_for, request, render_template

from src.controller.schemas import USER_SCHEMA
from src.login_manager import user_is_authenticated
from src.service import user_service
from src.view.forms.users_forms import EditUserForm, RegisterForm

USER_BLUEPRINT = Blueprint("user_controller", __name__)
USER_BLUEPRINT.before_request(user_is_authenticated)


@USER_BLUEPRINT.route("", methods=["GET"])
def list_users():
    schedule_tasks = user_service.get_all_users()
    return jsonify(
        {
            "rows": USER_SCHEMA.dump(schedule_tasks, many=True),
            "total": len(schedule_tasks),
        }
    )


@USER_BLUEPRINT.route("active/<user_id>", methods=["POST"])
def enable_disable_user(user_id):
    if user_service.get_current_user().admin_role:
        user_service.enable_disable_user(user_id)

        success_message = "Usuario editado"

        return redirect(
            url_for(
                "view_controller.user_list",
                success_message=success_message,
            )
        )


@USER_BLUEPRINT.route("update/<user_id>", methods=["POST"])
def update_user(user_id):
    form = EditUserForm(user_id)
    if form.validate_on_submit():
        user_service.edit(
            user_id,
            form.email.data,
            form.first_name.data,
            form.last_name.data,
            form.admin_role.data,
            form.password.data,
        )

    success_message = "Usuario editado exitosamente"
    return redirect(
        url_for(
            "view_controller.user_list",
            success_message=success_message,
        )
    )


@USER_BLUEPRINT.route("/register", methods=["GET"])
def register_user():
    return render_template("user_login_sign-up.html", form=RegisterForm(admin_role=False))


@USER_BLUEPRINT.route("/register-up", methods=["POST"])
def do_register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        user_service.save(
            form.email.data,
            form.first_name.data,
            form.last_name.data,
            form.admin_role.data,
            form.password.data,
        )

    success_message = "Usuario creado exitosamente"

    return redirect(
        url_for(
            "view_controller.user_list",
            success_message=success_message,
        )
    )