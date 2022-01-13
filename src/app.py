from http import HTTPStatus
from flask import Flask, jsonify, redirect, url_for

from src.encoders import CustomJSONEncoder
from src import controller
from src.translations import gettext, pretty_date
from src import logger
from src import config
from src import login_manager

app = Flask(__name__)

app.config["SECRET_KEY"] = config.secret_key

app.register_blueprint(controller.USER_BLUEPRINT, url_prefix="/user")
app.register_blueprint(controller.GEOMETRY_BLUEPRINT, url_prefix="/geometry")
app.register_blueprint(
    controller.EXECUTION_PLAN_BLUEPRINT, url_prefix="/execution_plan"
)
app.register_blueprint(controller.VIEW_BLUEPRINT, url_prefix="/view")
app.register_blueprint(controller.PUBLIC_VIEW_BLUEPRINT, url_prefix="/view")

app.jinja_env.globals.update(gettext=gettext)
app.jinja_env.globals.update(pretty_date=pretty_date)

login_manager.set_up_login(app)


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

if __name__ == "__main__":
    app.run(debug=True)
