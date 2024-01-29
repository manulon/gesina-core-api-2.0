from datetime import datetime

from sqlalchemy.orm import joinedload

from src.persistance import Geometry
from src.persistance.session import get_session
from src.service import file_storage_service
from werkzeug.utils import secure_filename

from src.service.file_storage_service import FileType


def create(form, user):
    file_field = form.file
    name = secure_filename(file_field.data.filename)
    description_field = form.description
    created_at = datetime.now()

    geometry = Geometry(
        name=name,
        description=description_field.data,
        user=user,
        created_at=created_at,
    )
    with get_session() as session:
        session.add(geometry)
        file = file_field.data
        file_storage_service.save_file(FileType.GEOMETRY, file, file.filename)

    return geometry


def get_geometries():
    geometries = []
    with get_session() as session:
        data = (
            session.query(Geometry)
            .order_by(Geometry.id.desc())
            .options(joinedload(Geometry.user))
            .all()
        )
        if data:
            geometries = data

    return geometries


def get_geometry(geometry_id):
    with get_session() as session:
        result = (
            session.query(Geometry).options(joinedload(Geometry.user)).get(geometry_id)
        )
        return result
    
def delete_geometry(geometry_id):
    try:
        geometry = get_geometry(geometry_id)
        file_storage_service.delete_geometry_file(geometry.name)
        with get_session() as session:
            session.delete(geometry)
            session.commit()
        return True
    except Exception as e:
        print("error while deleting geometry: " + geometry_id)
        print(e)
        raise e

def edit_geometry(
        geometry_id, 
        description=None
    ):
    geometry = get_geometry(geometry_id)
    with get_session() as session:
        session.add(geometry)
        geometry.description = description if description is not None else geometry.description
        session.commit()
    return get_geometry(geometry_id)
