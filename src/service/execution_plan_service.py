from src.persistance.execution_plan import ExecutionPlan, ExecutionPlanStatus
from src.persistance.session import get_session
from src.service import file_storage_service, user_service
from src.service.file_storage_service import FileType


def create(form):
    plan_name = form.plan_name.data
    geometry_id = form.geometry_option.data
    user = user_service.get_current_user()

    with get_session() as session:
        execution_plan = ExecutionPlan(
            plan_name=plan_name, geometry_id=geometry_id, user_id=user.id
        )
        session.add(execution_plan)
        session.commit()
        session.refresh(execution_plan)
        execution_plan_id = execution_plan.id
        geometry = execution_plan.geometry

        file_storage_service.copy_geometry_to(execution_plan_id, geometry.name)
        project_file_data = form.project_file.data
        file_storage_service.save_file(
            FileType.EXECUTION_PLANS,
            project_file_data,
            project_file_data.filename,
            execution_plan_id,
        )
        plan_file_data = form.plan_file.data
        file_storage_service.save_file(
            FileType.EXECUTION_PLANS,
            plan_file_data,
            plan_file_data.filename,
            execution_plan_id,
        )
        flow_file_data = form.flow_file.data
        file_storage_service.save_file(
            FileType.EXECUTION_PLANS,
            flow_file_data,
            flow_file_data.filename,
            execution_plan_id,
        )

        return execution_plan


def get_execution_plans():
    execution_plans = []
    with get_session() as session:
        data = session.query(ExecutionPlan).order_by(ExecutionPlan.id.desc()).all()
        if data:
            execution_plans = data

    return execution_plans


def get_execution_plan(execution_plan_id):
    with get_session() as session:
        return (
            session.query(ExecutionPlan).filter_by(id=execution_plan_id).one_or_none()
        )


def update_execution_plan_status(execution_plan_id, status: ExecutionPlanStatus):
    ep = get_execution_plan(execution_plan_id)

    with get_session() as session:
        session.add(ep)
        ep.status = status
