from http import HTTPStatus

import matplotlib
from flask import Flask, jsonify, redirect, url_for, render_template

import src
from src import config
from src import controller
from src import login_manager
from src.api import API_BLUEPRINT
from src.api.execution_plan_api import EXECUTION_PLAN_API_BLUEPRINT
from src.api.geometry_api import GEOMETRY_API_BLUEPRINT
from src.api.schedule_api import SCHEDULE_API_BLUEPRINT
from src.api.user_api import USER_API_BLUEPRINT
from src.encoders import CustomJSONEncoder
from src.translations import gettext, pretty_date

matplotlib.use("Agg")

app = Flask(__name__)

app.config["SECRET_KEY"] = config.secret_key

app.register_blueprint(controller.GEOMETRY_BLUEPRINT, url_prefix="/geometry")
app.register_blueprint(
    controller.EXECUTION_PLAN_BLUEPRINT, url_prefix="/execution_plan"
)
app.register_blueprint(controller.VIEW_BLUEPRINT, url_prefix="/view")
app.register_blueprint(controller.PUBLIC_VIEW_BLUEPRINT, url_prefix="/view")
app.register_blueprint(controller.SCHEDULE_TASK_BLUEPRINT, url_prefix="/schedule_task")
app.register_blueprint(controller.USER_BLUEPRINT, url_prefix="/user")

API_BLUEPRINT.register_blueprint(EXECUTION_PLAN_API_BLUEPRINT)
API_BLUEPRINT.register_blueprint(GEOMETRY_API_BLUEPRINT)
API_BLUEPRINT.register_blueprint(SCHEDULE_API_BLUEPRINT)
API_BLUEPRINT.register_blueprint(USER_API_BLUEPRINT)
app.register_blueprint(API_BLUEPRINT)

app.jinja_env.globals.update(gettext=gettext)
app.jinja_env.globals.update(pretty_date=pretty_date)

login_manager.set_up_login(app)
@app.route('/api_spec')
def swagger_ui():
    return render_template('swaggerui.html')

@app.route("/health-check")
def health_check():
    return jsonify({"status": "ok"}), HTTPStatus.OK

@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):
    print("no found")
    return redirect(url_for("view_controller.home")), HTTPStatus.MOVED_PERMANENTLY

@app.route('/list_routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(rule.methods),
            'url': str(rule),
        })
    return jsonify({'routes': routes})


app.json_encoder = CustomJSONEncoder

if __name__ == "__main__":
    src.migrate()
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5001)
