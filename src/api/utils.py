from flask import jsonify

from src.service import file_storage_service


def validate_fields(body, required_fields):
    missing_fields = [field for field in required_fields if field not in body or body.get(field) is None]
    return missing_fields


def validate_files_for_scheduled_task(body, missing_fields):
    files = body.get("files")
    existing_files = set(obj['name'] for obj in files)
    prj = body.get("project_file")
    plan = body.get("plan_file")
    if prj is None and "prj_template.txt" not in existing_files:
        missing_fields.append("project file")
    if plan is None and "plan_template.txt" not in existing_files:
        missing_fields.append("plan file")
    return missing_fields


def send_bad_request(message):
    response = jsonify({"message": message})
    response.status_code = 400
    return response


def get_file_if_present(body, field):
    name = body.get(field)
    if body.get(field):
        return file_storage_service.get_file(name)
    return None
