from datetime import datetime

from sqlalchemy.orm import joinedload

from src.persistance.execution_plan import ExecutionPlan, ExecutionPlanStatus
from src.persistance.session import get_session


def create(form):
    plan_name = form.plan_name.data
    geometry_id = form.geometry_option.data
    user_id = 1  # hardcode
    created_at = datetime.now()
    start_datetime = form.start_date.data
    end_datetime = form.end_date.data

    with get_session() as session:
        # TODO falta crear la carpeta de la ejecucion en minio y todos los archivos necesarios
        # flow_file_field = form.file
        # file_storage_service.save_flow(flow_file_field.data)
        execution_plan = ExecutionPlan(
            plan_name=plan_name,
            geometry_id=geometry_id,
            user_id=user_id,
            created_at=created_at,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=ExecutionPlanStatus.PENDING,
        )
        session.add(execution_plan)
        return execution_plan


def get_execution_plans():
    execution_plans = []
    with get_session() as session:
        data = (
            session.query(ExecutionPlan)
            .options(joinedload(ExecutionPlan.user))
            .options(joinedload(ExecutionPlan.geometry))
            .all()
        )
        if data:
            execution_plans = data

    return execution_plans


def get_execution_plan(execution_plan_id):
    with get_session() as session:
        result = (
            session.query(ExecutionPlan)
            .options(joinedload(ExecutionPlan.user))
            .options(joinedload(ExecutionPlan.geometry))
            .get(execution_plan_id)
        )
        return result
