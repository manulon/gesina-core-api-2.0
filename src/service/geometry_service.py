from datetime import datetime

from src.persistance import Geometry
from src.persistance.session import get_session
from src.service import file_storage_service
from src.service.exception.geometry_exception import GeometryMissingValue


def create(request):
    validate_creation_request(request)

    file = request.files["file"]
    name = file.filename
    form = request.form
    description = form["description"]
    user_id = 1  # hardcode
    created_at = datetime.now()

    geometry = Geometry(
        name=name, description=description, user_id=user_id, created_at=created_at
    )
    with get_session() as session:
        session.add(geometry)
        file_storage_service.save_geometry(file)

    return geometry


def validate_creation_request(request):
    form = request.form
    if not form:
        raise GeometryMissingValue("The form cannot be empty.")

    if not form["description"]:
        raise GeometryMissingValue("Description cannot be empty.")

    file_storage_service.validate_file(request.files)
