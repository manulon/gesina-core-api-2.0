from http import HTTPStatus
from flask import Flask, jsonify, redirect, url_for

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

app = Flask(__name__)


app.register_blueprint(BACKOFFICE_BLUEPRINT, url_prefix="/backoffice")
app.register_blueprint(BACKOFFICE_USER_BLUEPRINT, url_prefix="/backoffice_user")
app.register_blueprint(GEOMETRY_BLUEPRINT, url_prefix="/geometry")
app.register_blueprint(VIEW_BLUEPRINT, url_prefix="/view")


app.jinja_env.globals.update(gettext=gettext)
app.jinja_env.globals.update(pretty_date=pretty_date)
app.jinja_env.globals.update(current_user=current_user)


@app.route("/health-check")
def health_check():
    from src.tasks import add
    result = add.delay(1,2)
    try:
        return jsonify({"count": result.get()}), HTTPStatus.OK
    except Exception as e:
        print(e, flush=True)


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):
    return redirect(url_for("view_controller.home")), HTTPStatus.MOVED_PERMANENTLY


app.json_encoder = CustomJSONEncoder

set_up_exception_handlers(app)

if __name__ == "__main__":
    app.run(debug=True)
