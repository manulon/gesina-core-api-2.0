from flask_login import LoginManager, current_user

login_manager = LoginManager()


def set_up_login(app):
    login_manager.init_app(app)
    login_manager.login_view = "public_view_controller.login"


def user_is_authenticated():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
