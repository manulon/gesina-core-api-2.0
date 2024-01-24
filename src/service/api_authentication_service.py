from flask_httpauth import HTTPBasicAuth

from src.persistance.session import get_session
from src.persistance.user import User

from src.service import (
    user_service
)

from flask import  jsonify


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return user_service.get_user_by_email_and_password(username,password)

@auth.error_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized access'}), 401

@auth.login_required
def before_api_request():
    pass

