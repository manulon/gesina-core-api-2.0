from src.persistance.execution_plan import ExecutionPlan, ExecutionPlanStatus
from src.persistance.session import get_session
from src.service import file_storage_service, user_service
from src.service.file_storage_service import FileType
from sqlalchemy import and_


def create_from_form(form):
    plan_name = form.plan_name.data
    geometry_id = form.geometry_option.data
    user = user_service.get_current_user()
    project_file_data = form.project_file.data
    plan_file_data = form.plan_file.data
    flow_file_data = form.flow_file.data
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


def create_from_scheduler(
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
    return create(
        execution_plan_name,
        geometry_id,
        user,
        project_name,
        project_file,
        plan_name,
        plan_file,
        flow_name,
        flow_file,
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


def get_execution_plans_by_dates(date_from, date_to):
    with get_session() as session:
        return (
            session.query(ExecutionPlan)
            .filter(
                and_(
                    ExecutionPlan.created_at > date_from,
                    ExecutionPlan.created_at < date_to,
                )
            )
            .all()
        )


def get_execution_plans_grouped_by_interval(interval):
    with get_session() as session:
        query = f"""SELECT COUNT(*) AS QUANTITY,
                extract(day from created_at) AS DAY, 
                extract(month from created_at) AS MONTH, 
                extract(year from created_at) AS YEAR 
                FROM gesina.execution_plan WHERE created_at >= CURRENT_DATE - INTERVAL '{interval}' 
                GROUP BY DAY, MONTH, YEAR 
                ORDER BY YEAR, MONTH, DAY
                """

        return session.execute(query)


def update_execution_plan_status(execution_plan_id, status: ExecutionPlanStatus):
    execution_plan = get_execution_plan(execution_plan_id)

    with get_session() as session:
        session.add(execution_plan)
        execution_plan.status = status


def update_finished_execution_plan(execution_plan_id, start_datetime, end_datetime):
    execution_plan = get_execution_plan(execution_plan_id)

    with get_session() as session:
        session.add(execution_plan)
        execution_plan.status = ExecutionPlanStatus.FINISHED
        execution_plan.start_datetime = start_datetime
        execution_plan.end_datetime = end_datetime
