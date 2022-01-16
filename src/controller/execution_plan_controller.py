import sqlalchemy
from flask import Blueprint, jsonify, render_template, request
from flask import Blueprint, jsonify

from src.login_manager import user_is_authenticated
from src.service import execution_plan_service

EXECUTION_PLAN_BLUEPRINT = Blueprint("execution_plan_controller", __name__)


@EXECUTION_PLAN_BLUEPRINT.route("", methods=["POST"])
def save():
    form = ExecutionPlanForm()
    try:
        if form.validate_on_submit():
            execution_plan = execution_plan_service.create(form)
            success_message = f"Simulación #{str(execution_plan.id)} creada con éxito."
            return render_template("execution_plan_list.html", success=success_message)

        return render_template(
            "execution_plan.html", form=form, errors=form.get_errors()
        )
    except sqlalchemy.exc.IntegrityError as database_error:
        logger.error(database_error)
        error_message = "Error guardando información en la base de datos."

        return render_template(
            "execution_plan.html", form=form, errors=[error_message], **request.form
        )
    except FileUploadError as file_error:
        logger.error(file_error.message, file_error)
        error_message = "Error cargando archivo. Intente nuevamente."

        return render_template(
            "execution_plan.html", form=form, errors=[error_message], **request.form
        )
EXECUTION_PLAN_BLUEPRINT.before_request(user_is_authenticated)


@EXECUTION_PLAN_BLUEPRINT.route("", methods=["GET"])
def list_execution_plans():
    execution_plans = execution_plan_service.get_execution_plans()

    response_list = []
    for execution_plan in execution_plans:
        user = execution_plan.user
        geometry = execution_plan.geometry
        execution_plan_row = {
            "id": execution_plan.id,
            "geometry": geometry.description,
            "user": user.full_name,
            "created_at": execution_plan.created_at.strftime("%d/%m/%Y"),
            "status": execution_plan.status,
        }
        response_list.append(execution_plan_row)

    return jsonify({"rows": response_list, "total": len(response_list)})
