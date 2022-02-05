from datetime import datetime

from sqlalchemy.orm import joinedload

from src.persistance.execution_plan import ExecutionPlan, ExecutionPlanStatus
from src.persistance.session import get_session
from src.service import file_storage_service, user_service


def create(form):
    plan_name = form.plan_name.data
    geometry_id = form.geometry_option.data
    user = user_service.get_current_user()
    created_at = datetime.now()

    with get_session() as session:
        execution_plan = ExecutionPlan(
            plan_name=plan_name,
            geometry_id=geometry_id,
            user_id=user.id,
            created_at=created_at,
            status=ExecutionPlanStatus.PENDING,
        )
        session.add(execution_plan)
        session.commit()
        session.refresh(execution_plan)
        execution_plan_id = execution_plan.id
        geometry = execution_plan.geometry

        project_file_field = form.project_file
        plan_file_field = form.plan_file
        flow_file_field = form.flow_file

        file_storage_service.copy_geometry_to(execution_plan_id, geometry.name)
        file_storage_service.save_execution_file(
            project_file_field.data, execution_plan_id
        )
        file_storage_service.save_execution_file(
            plan_file_field.data, execution_plan_id
        )
        file_storage_service.save_execution_file(
            flow_file_field.data, execution_plan_id
        )

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
