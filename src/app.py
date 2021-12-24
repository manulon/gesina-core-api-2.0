from http import HTTPStatus
from flask import Flask, jsonify, redirect, url_for

from src.controller.execution_plan_controller import EXECUTION_PLAN_BLUEPRINT
from src.encoders import CustomJSONEncoder
from src.service.backoffice_user_service import current_user
from src.controller import (
    BACKOFFICE_BLUEPRINT,
    BACKOFFICE_USER_BLUEPRINT,
    GEOMETRY_BLUEPRINT,
    VIEW_BLUEPRINT,
)
from src.exception_handler import set_up_exception_handlers
from src.translations import gettext, pretty_date
from src import logger
from src import config


app = Flask(__name__)

app.config["SECRET_KEY"] = config.secret_key

app.register_blueprint(BACKOFFICE_BLUEPRINT, url_prefix="/backoffice")
app.register_blueprint(BACKOFFICE_USER_BLUEPRINT, url_prefix="/backoffice_user")
app.register_blueprint(GEOMETRY_BLUEPRINT, url_prefix="/geometry")
app.register_blueprint(EXECUTION_PLAN_BLUEPRINT, url_prefix="/execution_plan")
app.register_blueprint(VIEW_BLUEPRINT, url_prefix="/view")


app.jinja_env.globals.update(gettext=gettext)
app.jinja_env.globals.update(pretty_date=pretty_date)
app.jinja_env.globals.update(current_user=current_user)


@app.route("/health-check")
def health_check():
    return jsonify({"status": "ok"}), HTTPStatus.OK


@app.route("/test")
def test():
    from src.tasks import simulate, error_handler

    logger.info("Start simulation")
    simulate.apply_async(link_error=error_handler.s())
    try:
        logger.info("Receiving result")
        return jsonify({"status": "ok"}), HTTPStatus.CREATED
    except Exception as e:
        logger.error(e)


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):
    return redirect(url_for("view_controller.home")), HTTPStatus.MOVED_PERMANENTLY


app.json_encoder = CustomJSONEncoder

set_up_exception_handlers(app)

if __name__ == "__main__":
    app.run(debug=True)
