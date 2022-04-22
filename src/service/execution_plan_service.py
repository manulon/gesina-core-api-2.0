from src.persistance.execution_plan import ExecutionPlan, ExecutionPlanStatus
from src.persistance.session import get_session
from src.service import file_storage_service, user_service
from src.service.file_storage_service import FileType


def create_from_form(form):
    plan_name = form.plan_name.data
    geometry_id = form.geometry_option.data
    user = user_service.get_current_user()
    project_file_data = form.project_file.data
    plan_file_data = form.project_file.plan_file
    flow_file_data = form.project_file.flow_file
    return create(
        plan_name,
        geometry_id,
        user,
        project_file_data.filename,
        project_file_data,
        plan_file_data.filename,
        plan_file_data,
        flow_file_data.filename,
        flow_file_data,
    )


def create(
    execution_plan_name,
    geometry_id,
    user,
    project_name,
    project_file,
    plan_name,
    plan_file,
    flow_name,
    flow_file,
):
    with get_session() as session:
        execution_plan = ExecutionPlan(
            plan_name=execution_plan_name, geometry_id=geometry_id, user_id=user.id
        )
        session.add(execution_plan)
        session.commit()
        session.refresh(execution_plan)
        execution_plan_id = execution_plan.id
        geometry = execution_plan.geometry

        file_storage_service.copy_geometry_to(execution_plan_id, geometry.name)

        file_storage_service.save_file(
            FileType.EXECUTION_PLAN,
            project_file,
            project_name,
            execution_plan_id,
        )

        file_storage_service.save_file(
            FileType.EXECUTION_PLAN,
            plan_file,
            plan_name,
            execution_plan_id,
        )

        file_storage_service.save_file(
            FileType.EXECUTION_PLAN,
            flow_file,
            flow_name,
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
