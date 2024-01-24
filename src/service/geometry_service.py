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
        id=None, 
        name=None,
        description=None,
        created_at=None,
        user_id=None,
        user=None
    ):
    geometry = get_geometry(geometry_id)
    with get_session() as session:
        session.add(geometry)
        geometry.name = name if name is not None else geometry.name
        geometry.description = description if description is not None else geometry.description
        geometry.created_at = created_at if created_at is not None else geometry.created_at
        #geometry.user_id = user_id if user_id is not None else geometry.user_id
        #geometry.user = user if user is not None else geometry.user
        session.commit()
    return get_geometry(geometry_id)
