from datetime import datetime

from sqlalchemy.orm import joinedload
from src.exception.delete_geometry_exception import GeometryInUseException

from src.persistance import Geometry
from src.persistance.session import get_session
from src.service import file_storage_service
from werkzeug.utils import secure_filename

from src.service.file_storage_service import FileType
from src.persistance.execution_plan import ExecutionPlan
from src.persistance.scheduled_task import ScheduledTask

def create(file_name, file_data, description, user):
    name = secure_filename(file_name)
    created_at = datetime.now()

    geometry = Geometry(
        name=name,
        description=description,
        user=user,
        created_at=created_at,
    )

    try:
        with get_session() as session:
            session.add(geometry)
            file_storage_service.save_file(FileType.GEOMETRY, file_data, file_name)
            return geometry
        
    except Exception as e:
        raise e


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
        if not geometry:
            raise Exception(f"Geometry with id {geometry_id} does not exist")
        geometry_name = geometry.name
        with get_session() as session:
            execution_plan = session.query(ExecutionPlan).filter(ExecutionPlan.geometry_id == geometry_id).first()
            scheduled_task = session.query(ScheduledTask).filter(ScheduledTask.geometry_id == geometry_id).first()
            if execution_plan == None and scheduled_task == None:
                session.delete(geometry)
                session.commit()
                file_storage_service.delete_geometry_file(geometry_name)
                return True
            else:
                raise GeometryInUseException(geometry_id)
    except Exception as e:
        print("Error while deleting geometry: " + geometry_id)
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
