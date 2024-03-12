from src.persistance.execution_plan import (
    ExecutionPlan,
    ExecutionPlanStatus,
    ExecutionPlanOutput,
)
from src.persistance.session import get_session
from src.persistance.user import User
from src.persistance.scheduled_task import ExecutionPlanScheduleTaskMapping
from src.service import file_storage_service, user_service, geometry_service
from src.service.file_storage_service import FileType
from sqlalchemy import and_, func

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
    if e is None:
        raise Exception(f"Execution plan with id {execution_plan_id} does not exist")
    execution_plan = create_copy(e.plan_name, e.geometry, e.user, e.execution_plan_output_list)
    file_storage_service.copy_execution_files(execution_plan_id, execution_plan.id)
    return execution_plan

def create_from_json(execution_plan, user_id):
    return create(
        execution_plan.get('plan_name'),
        execution_plan.get('geometry_id'),
        user_id,
        execution_plan.get('project_file', {}).get('filename'),
        None if execution_plan.get('project_file', {}).get('data') is None else io.BytesIO(execution_plan.get('project_file', {}).get('data').encode('utf-8')),
        execution_plan.get('plan_file', {}).get('filename'),
        None if execution_plan.get('plan_file', {}).get('data') is None else io.BytesIO(execution_plan.get('plan_file', {}).get('data').encode('utf-8')),
        execution_plan.get('flow_file', {}).get('filename'),
        None if execution_plan.get('flow_file', {}).get('data') is None else io.BytesIO(execution_plan.get('flow_file', {}).get('data').encode('utf-8')),
        None if execution_plan.get('restart_file', {}).get('data') is None else io.BytesIO(execution_plan.get('restart_file', {}).get('data').encode('utf-8')),
        [
            ExecutionPlanOutput(
                river=d.get("river"),
                reach=d.get("reach"),
                river_stat=d.get("river_stat")
            )
            for d in execution_plan.get('execution_output_list', [])
        ],
        restart_name=execution_plan.get('restart_file', {}).get('filename')
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
                stage_datum=ps.stage_datum
            )
            for ps in plan_series_list
        ],
    )
    if use_restart:
        file_storage_service.copy_restart_file_to(execution_plan.id, schedule_task_id)

    with get_session() as session:
        mapping = ExecutionPlanScheduleTaskMapping(
            scheduled_task_id=schedule_task_id,
            execution_id=execution_plan.id
        )
        session.add(mapping)
        session.commit()
        session.refresh(mapping)

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
        restart_name=None
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

        if project_file is not None:
            file_storage_service.save_file(
                FileType.EXECUTION_PLAN,
                project_file,
                project_name,
                execution_plan_id,
            )
        else:
            file_storage_service.copy_execution_file(project_name, execution_plan_id)

        if plan_file is not None:
            file_storage_service.save_file(
                FileType.EXECUTION_PLAN,
                plan_file,
                plan_name,
                execution_plan_id,
            )
        else:
            file_storage_service.copy_execution_file(plan_name,execution_plan_id)

        if flow_file is not None:
            file_storage_service.save_file(
                FileType.EXECUTION_PLAN,
                flow_file,
                flow_name,
                execution_plan_id,
            )
        else:
            file_storage_service.copy_execution_file(flow_name,execution_plan_id)
        restart_file_name = "restart_file.rst"
        if not isinstance(restart_file, io.BytesIO) and restart_file is not None:
            restart_file_name = restart_file.filename

        if restart_file is not None:
            file_storage_service.save_file(
                FileType.EXECUTION_PLAN,
                restart_file,
                restart_file_name,
                execution_plan_id,
            )
        elif restart_name is not None:
            file_storage_service.copy_execution_file(restart_name, execution_plan_id, restart_file_name)

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
    execution_plan = get_execution_plan(execution_plan_id)
    if execution_plan is None:
        raise Exception(f"Execution plan with id {execution_plan_id} does not exist")
    with get_session() as session:
        session.delete(execution_plan)
        session.commit()
    file_storage_service.delete_execution_files(execution_plan_id)
    return True   

def get_execution_plans(plan_name=None, user_first_name=None, user_last_name=None, status=None, date_from=None,
                        date_to=None):
    execution_plans = []
    with get_session() as session:

        query = session.query(ExecutionPlan).order_by(ExecutionPlan.id.desc())

        if plan_name is not None:
            query = query.filter(ExecutionPlan.plan_name.like(f"%{plan_name}%"))
        if user_first_name is not None or user_last_name is not None:
            query = query.join(User, aliased=True)
            if user_first_name is not None:
                query = query.filter(func.lower(User.first_name).like(func.lower(f"%{user_first_name}%")))
            if user_last_name is not None:
                query = query.filter(func.lower(User.last_name).like(func.lower(f"%{user_last_name}%")))
        if status is not None and status != "":
            query = query.filter(ExecutionPlan.status == status)
        if date_from is not None:
            query = query.filter(ExecutionPlan.start_datetime >= date_from)
        if date_to is not None:
            query = query.filter(ExecutionPlan.start_datetime <= date_to)

        data = query.all()
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

def get_execution_plans_json(offset=0, limit=9999, date_from=None, date_to=None, user_first_name=None,
                             user_last_name=None, name=None, status=None):
    execution_plans = get_execution_plans(plan_name=name, user_first_name=user_first_name,
                                          user_last_name=user_last_name, status=status, date_from=date_from,
                                          date_to=date_to)
    total_rows = len(execution_plans)

    response_list = []
    for execution_plan in execution_plans[offset: offset + limit]:
        user = execution_plan.user
        execution_files = [
            f.object_name
            for f in file_storage_service.list_execution_files(
                FileType.EXECUTION_PLAN, execution_plan.id
            )
        ]
        execution_plan_row = {
            "id": execution_plan.id,
            "plan_name": execution_plan.plan_name,
            "user": user.full_name,
            "created_at": execution_plan.created_at.strftime("%d/%m/%Y"),
            "status": execution_plan.status,
            "execution_files": execution_files
        }
        response_list.append(execution_plan_row)
    return response_list

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

def edit_execution_plan(execution_plan_id, plan_name=None, geometry_id=None, project_file=None, plan_file=None,
                        flow_file=None, restart_file=None, execution_plan_output=None):
    execution_plan = get_execution_plan(execution_plan_id)
    with get_session() as session:
        session.add(execution_plan)
        if execution_plan_output is not None:
            new_output_list = []
            for d in execution_plan_output:
                if d.get("river") is None or d.get("reach") is None or d.get("river_stat") is None:
                    raise Exception("Execution plan output does not contain river, river_stat or reach")

                new_output_list.append(
                    ExecutionPlanOutput(
                        river=d.get("river"), reach=d.get("reach"), river_stat=d.get("river_stat"),
                        execution_plan_id=execution_plan_id
                    )
                )
            session.query(ExecutionPlanOutput).filter_by(execution_plan_id=execution_plan_id).delete()
            session.commit()
            session.refresh(execution_plan)
            execution_plan.execution_plan_output_list = new_output_list
        execution_plan.plan_name = plan_name if plan_name is not None else execution_plan.plan_name
        if geometry_id is not None:
            new_geometry_filename = str(geometry_service.get_geometry(int(geometry_id)))

            if new_geometry_filename == "None":
                raise Exception(f"Geometry with id {geometry_id} does not exist")
            old_geometry_filename = execution_plan.geometry
            file_storage_service.copy_geometry_to(execution_plan_id, new_geometry_filename)
            file_storage_service.delete_execution_file(execution_plan_id, old_geometry_filename)
            execution_plan.geometry_id = geometry_id
        session.commit()
    for file in [project_file, plan_file, flow_file, restart_file]:
        if file is not None:
            try:
                file_storage_service.delete_execution_file_for_type(execution_plan_id, file)
                file_storage_service.copy_execution_file(file, execution_plan_id)
                file_storage_service.delete_file(file)
            except Exception as e:
                print(f"error while copying execution file: {file}  to folder: {execution_plan_id}")
                raise e
    return get_execution_plan(execution_plan_id)
