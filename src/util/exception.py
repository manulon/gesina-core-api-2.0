import flask
from flask import json, url_for
from werkzeug.exceptions import HTTPException

from src.app import app


class BasicException(Exception):
    pass


class UnauthorizedException(BasicException):
    pass


class ForbiddenException(BasicException):
    pass


@app.errorhandler(UnauthorizedException)
def handle_exception(e):
    return "Error"
