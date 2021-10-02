import uuid

from flask import request


def get_app_user_by_username(username):
    return None


def get_backoffice_user_by_session_id(session_id):
    return None


def clear_session_id(session_id):
    backoffice_user = get_backoffice_user_by_session_id(session_id)
    backoffice_user.update(session_id=None)
    return backoffice_user.reload()


def create_session_id(username, password):
    backoffice_user = get_app_user_by_username(username)
    if backoffice_user is None or backoffice_user.password != password:
        return None
    backoffice_user.update(session_id=uuid.uuid4())
    return backoffice_user.reload().session_id


def current_user():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return None
    return get_backoffice_user_by_session_id(session_id)
