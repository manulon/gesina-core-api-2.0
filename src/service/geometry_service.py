from datetime import datetime

from sqlalchemy.orm import joinedload

from src.persistance import Geometry
from src.persistance.session import get_session
from src.service import file_storage_service
from werkzeug.utils import secure_filename


def create(form):
    file_field = form.file
    name = secure_filename(file_field.data.filename)
    description_field = form.description
    user_id = 1  # hardcode
    created_at = datetime.now()

    geometry = Geometry(
        name=name,
        description=description_field.data,
        user_id=user_id,
        created_at=created_at,
    )
    with get_session() as session:
        session.add(geometry)
        file_storage_service.save_geometry(file_field.data)

    return geometry


def get_geometries():
    geometries = []
    with get_session() as session:
        data = session.query(Geometry).options(joinedload(Geometry.user)).all()
        if data:
            geometries = data

    return geometries


def get_geometry(geometry_id):
    with get_session() as session:
        result = (
            session.query(Geometry).options(joinedload(Geometry.user)).get(geometry_id)
        )
        return result
