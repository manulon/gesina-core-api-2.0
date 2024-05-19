import re

from flask import jsonify

from src.service import file_storage_service


def validate_fields(body, required_fields):
    missing_fields = [field for field in required_fields if field not in body or body.get(field) is None]
    return missing_fields


def get_hecras_file_type(filename):
    if 'plan_template' in filename:
        return "plan_file"
    if "prj_template" in filename:
        return 'project_file'
    patterns = {
        "plan_file": r'^.+\.p\d{2}$',
        "flow_file": r'^.+\.(u|f|q)\d{2}$',
        "project_file": r'^.+\.prj$',
        "restart_file": r'^.+\.rst$'
    }
    for file_type, pattern in patterns.items():
        regex = re.compile(pattern)
        if regex.match(filename):
            return file_type

    return None

def validate_files_for_scheduled_task(body, missing_fields):
    files = body.get("files")
    try:
        existing_files = set(obj['type'] for obj in files)
    except KeyError as e:
        raise Exception("type is a mandatory field for each file")
    if "project_file" not in existing_files:
        missing_fields.append("project file")
    if "plan_file" not in existing_files:
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
