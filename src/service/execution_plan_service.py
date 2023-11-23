from src.persistance.execution_plan import (
    ExecutionPlan,
    ExecutionPlanStatus,
    ExecutionPlanOutput,
)
from src.persistance.session import get_session
from src.service import file_storage_service, user_service
from src.service.file_storage_service import FileType
from sqlalchemy import and_
import io


def create_from_form(form):
    plan_name = form.plan_name.data
    geometry_id = form.geometry_option.data
    user = user_service.get_current_user()
    project_file_data = form.project_file.data
    plan_file_data = form.plan_file.data
    flow_file_data = form.flow_file.data
    restart_file_data = form.restart_file.data
    execution_plan_output_list_data = form.execution_plan_output_list.data
    return create(
        plan_name,
        geometry_id,
        user.id,
        project_file_data.filename,
        project_file_data,
        plan_file_data.filename,
        plan_file_data,
        flow_file_data.filename,
        flow_file_data,
        restart_file_data,
        [
            ExecutionPlanOutput(
                river=d["river"], reach=d["reach"], river_stat=d["river_stat"]
            )
            for d in execution_plan_output_list_data
        ],
    )


def copy_execution_plan(execution_plan_id):
    e = get_execution_plan(execution_plan_id)
    execution_plan = create_copy(e.plan_name, e.geometry, e.user, e.execution_plan_output_list)
    file_storage_service.copy_execution_files(execution_plan_id, execution_plan.id)
    return execution_plan



def create_from_json(execution_plan):
    return create(
        execution_plan.get('plan_name'),
        execution_plan.get('geometry_id'),
        execution_plan.get('user_id'),
        execution_plan.get('project_file', {}).get('filename'),
        io.BytesIO(execution_plan.get('project_file', {}).get('data').encode('utf-8')),
        execution_plan.get('plan_file', {}).get('filename'),
        io.BytesIO(execution_plan.get('plan_file', {}).get('data').encode('utf-8')),
        execution_plan.get('flow_file', {}).get('filename'),
        io.BytesIO(execution_plan.get('flow_file', {}).get('data').encode('utf-8')),
        io.BytesIO(execution_plan.get('restart_file', {}).get('data').encode('utf-8')),
        [
            ExecutionPlanOutput(
                river=d.get("river"),
                reach=d.get("reach"),
                river_stat=d.get("river_stat")
            )
            for d in execution_plan.get('output_list_data', [])
        ]
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
        use_restart,
        schedule_task_id,
        plan_series_list,
):
    execution_plan = create(
        execution_plan_name,
        geometry_id,
        user.id,
        project_name,
        project_file,
        plan_name,
        plan_file,
        flow_name,
        flow_file,
        execution_plan_output_list=[
            ExecutionPlanOutput(
                river=ps.river,
                reach=ps.reach,
                river_stat=ps.river_stat,
                stage_series_id=ps.stage_series_id,
                flow_series_id=ps.flow_series_id,
            )
            for ps in plan_series_list
        ],
    )
    if use_restart:
        file_storage_service.copy_restart_file_to(execution_plan.id, schedule_task_id)

    return execution_plan


def create(
        execution_plan_name,
        geometry_id,
        user_id,
        project_name,
        project_file,
        plan_name,
        plan_file,
        flow_name,
        flow_file,
        restart_file=None,
        execution_plan_output_list=None,
):
    with get_session() as session:
        execution_plan = ExecutionPlan(
            plan_name=execution_plan_name,
            geometry_id=geometry_id,
            user_id=user_id,
            execution_plan_output_list=execution_plan_output_list,
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
        restart_file_name = "restart_file.rst"
        if not isinstance(restart_file, io.BytesIO):
            restart_file_name = restart_file.filename


        if restart_file:
            file_storage_service.save_file(
                FileType.EXECUTION_PLAN,
                restart_file,
                restart_file_name,
                execution_plan_id,
            )

        return execution_plan


def create_copy(execution_plan_name,
                geometry_id,
                user,
                execution_plan_output_list):
    with get_session() as session:
        execution_plan = ExecutionPlan(
            plan_name=execution_plan_name,
            geometry_id=geometry_id.id,
            user_id=user.id,
            execution_plan_output_list=execution_plan_output_list,
        )
        session.add(execution_plan)
        session.commit()
        session.refresh(execution_plan)
        execution_plan_id = execution_plan.id
        geometry = execution_plan.geometry

        file_storage_service.copy_geometry_to(execution_plan_id, geometry.name)
        return execution_plan


def delete_execution_plan(execution_plan_id):
    try:
        execution_plan = get_execution_plan(execution_plan_id)
        with get_session() as session:
            session.delete(execution_plan)
            session.commit()
        return True
    except Exception as e:
        print(e)
        return False

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
