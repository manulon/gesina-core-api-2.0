from flask import Blueprint, url_for

from src.service.api_authentication_service import before_api_request

API_BLUEPRINT = Blueprint("api", __name__, url_prefix="/api")
API_BLUEPRINT.before_request(before_api_request)


@API_BLUEPRINT.get("/")
def home():
    return {"status": "ok"}
