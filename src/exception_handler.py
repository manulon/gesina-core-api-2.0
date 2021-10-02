from http import HTTPStatus


from src.util.exception import (
    UnauthorizedException,
    ForbiddenException
)


def set_up_exception_handlers(app):
    @app.errorhandler(UnauthorizedException)
    def handle_exception(_):
        return "", HTTPStatus.UNAUTHORIZED

    @app.errorhandler(ForbiddenException)
    def handle_forbidden(_):
        return "", HTTPStatus.FORBIDDEN
