from flask_wtf.file import FileField
from sqlalchemy import func

from src.persistance.scheduled_task import ScheduledTask, ExecutionPlanScheduleTaskMapping, BorderCondition, PlanSeries
from src.persistance import User
from src.persistance.session import get_session
from src.service import project_file_service, plan_file_service, file_storage_service, execution_plan_service
from src.service.exception.file_exception import FileUploadError
from src.service.file_storage_service import save_restart_file, FileType
from src.service.initial_flow_service import create_initial_flows_from_form
from src.service.user_service import get_current_user
from src.service import initial_flow_service
from src.service import border_series_service
from src.service import plan_series_service


def contains_restart_file(objects):
    for obj in objects:
        if 'restart_file.rst' in obj['name']:
            return True
    return False


def create(params, start_condition_type, restart_file_data, project_file_data, plan_file_data, files = []):
    with get_session() as session:
        scheduled_task = ScheduledTask(**params)
        session.add(scheduled_task)

        session.commit()
        session.refresh(scheduled_task)
        if start_condition_type == "restart_file" and not contains_restart_file(files):
            save_restart_file(restart_file_data, scheduled_task.id)
        if len(files) > 0:
            for file in files:
                name = file["name"]
                contentB64 = file["content"]
                file_storage_service.upload_from_base64(scheduled_task.id,name,contentB64)
        project_file_service.process_project_template(
            project_file_data, scheduled_task.id
        )
        plan_file_service.process_plan_template(plan_file_data, scheduled_task.id)

        return scheduled_task


def update(_id, form):
    with get_session() as session:
        schedule_config = session.query(ScheduledTask).filter_by(id=_id).one_or_none()
        schedule_config.frequency = form.frequency.data
        schedule_config.calibration_id = form.calibration_id.data
        schedule_config.calibration_id_for_simulations = (
            form.calibration_id_for_simulations.data
        )
        schedule_config.name = form.name.data
        schedule_config.description = form.description.data
        schedule_config.geometry_id = form.geometry_id.data
        schedule_config.start_datetime = form.start_datetime.data
        if form.enabled.data:
            if not file_storage_service.is_project_template_present(
                    _id) or not file_storage_service.is_plan_template_present(
                _id) or not file_storage_service.is_restart_file_present(_id):
                raise FileUploadError("Es mandatorio subir todos los archivos para habilitar la ejecución")
        schedule_config.enabled = form.enabled.data
        schedule_config.observation_days = form.observation_days.data
        schedule_config.forecast_days = form.forecast_days.data
        schedule_config.start_condition_type = form.start_condition_type.data
        border_series_service.update_series_list(session, _id, border_series_service.retrieve_series(form, _id))
        plan_series_service.update_plan_series_list(session, _id, plan_series_service.retrieve_plan_series(form, _id))

        if form.start_condition_type.data == "restart_file" and form.restart_file.data:
            save_restart_file(form.restart_file.data, schedule_config.id)
        else:
            initial_flow_service.update_initial_flows(session, _id, initial_flow_service.retrieve_initial_flows_from_form(form, _id))

        project_file_service.process_project_template(form.project_file.data, _id)
        plan_file_service.process_plan_template(form.plan_file.data, _id)
        session.add(schedule_config)


def _create_objects(old_objects, new_objects, create_func, _id=None):
    if not callable(create_func):
        raise ValueError("The create function provided is not callable")

    if old_objects == []:
        return create_func(new_objects, _id)


def _update_objects(old_objects, new_objects, update_func, attr_name, _id=None):
    if not callable(update_func):
        raise ValueError("The update function provided is not callable")

    for new_object in new_objects:
        if not new_object.get("id"):
            if attr_name == "border_conditions":
                border_series_service.add_series_to_scheduled_task(new_object, _id)
            elif attr_name == "plan_series_list":
                plan_series_service.add_series_to_scheduled_task(new_object,_id)
            elif attr_name == "initial_flows":
                initial_flow_service.add_initial_flow_to_scheduled_task(new_object,_id)
        else:
            for obj in old_objects:
                try:
                    if obj.id == new_object["id"]:
                        update_func(obj, new_object)
                except KeyError as ke:
                    error_msg = f"MSG: You must specify the {obj.__class__.__name__} ID to edit it - ERROR: {ke}"
                    raise KeyError(error_msg) from ke
    return


def update_objects(schedule_config, old_objects, new_objects, update_func, create_func, attr_name, _id=None):
    if old_objects == []:
        setattr(
            schedule_config,
            attr_name,
            _create_objects(
                old_objects,
                new_objects,
                create_func,
                _id
            )
        )
    else:
        _update_objects(old_objects, new_objects, update_func, attr_name, _id)


def update_from_json(_id=None, **params):
    with get_session() as session:
        schedule_config = session.query(ScheduledTask).filter_by(id=_id).one_or_none()
        if not schedule_config:
            raise Exception(f"Scheduled task with id {_id} not found")
        for key, value in params.items():
            if value is not None:
                if key == 'border_conditions':
                    update_objects(
                        schedule_config,
                        schedule_config.border_conditions,
                        value,
                        border_series_service.update_border_condition,
                        border_series_service.process_series_json,
                        'border_conditions',
                        _id
                    )
                elif key == 'plan_series_list':
                    update_objects(
                        schedule_config,
                        schedule_config.plan_series_list,
                        value,
                        plan_series_service.update_plan_series,
                        plan_series_service.process_plan_series_json,
                        'plan_series_list',
                        _id
                    )
                elif key == 'initial_flows':
                    update_objects(
                        schedule_config,
                        schedule_config.initial_flows,
                        value,
                        initial_flow_service.update_initial_flow,
                        initial_flow_service.process_initial_flows_json,
                        'initial_flows',
                        _id
                    )
                elif key == 'enabled':
                    if value is True:
                        if not file_storage_service.is_project_template_present(
                                _id) or not file_storage_service.is_plan_template_present(
                            _id) or not file_storage_service.is_restart_file_present(_id):
                            raise FileUploadError("You must upload all the required files to enable execution")
                    setattr(schedule_config, key, value)
                else:
                    setattr(schedule_config, key, value)
        session.add(schedule_config)


def update_files(scheduled_task_id, project_file=None, plan_file=None, restart_file=None):
    project_path = None
    plan_path = None
    restart_file_path = None
    if project_file != None:
        project_path = project_file_service.process_project_template(project_file, scheduled_task_id)
    if plan_file != None:
        plan_path = plan_file_service.process_plan_template(plan_file, scheduled_task_id)
    if restart_file != None:
        restart_file_path = save_restart_file(restart_file, scheduled_task_id)
    return project_path, plan_path, restart_file_path


def create_from_form(form, border_conditions, plan_series):
    params = {
        "frequency": form.frequency.data,
        "calibration_id": form.calibration_id.data,
        "calibration_id_for_simulations": form.calibration_id_for_simulations.data,
        "enabled": form.enabled.data,
        "name": form.name.data,
        "description": form.description.data,
        "geometry_id": form.geometry_id.data,
        "start_datetime": form.start_datetime.data,
        "start_condition_type": form.start_condition_type.data,
        "observation_days": form.observation_days.data,
        "forecast_days": form.forecast_days.data,
        "user": get_current_user(),
        "border_conditions": border_conditions,
        "plan_series_list": plan_series,
    }
    if form.start_condition_type.data == "initial_flows":
        params["initial_flows"] = create_initial_flows_from_form(form)

    start_condition_type = form.start_condition_type.data
    restart_file_data = form.restart_file.data
    project_file_data = form.project_file.data
    plan_file_data = form.plan_file.data

    if form.enabled.data:
        if form.start_condition_type.data == "restart_file":
            if restart_file_data.filename == '':
                raise FileUploadError("Es mandatorio subir todos los archivos para habilitar la ejecución")
        if project_file_data.filename == '' or plan_file_data.filename == '':
            raise FileUploadError("Es mandatorio subir todos los archivos para habilitar la ejecución")

    return create(params, start_condition_type, restart_file_data, project_file_data, plan_file_data)


def get_schedule_tasks(name=None, user_first_name=None, user_last_name=None, start_condition_type=None, date_from=None,
                       date_to=None, enabled=None, frequency=None, calibration_id=None,
                       calibration_id_for_simulations=None, reduced=False):
    with get_session() as session:
        query = session.query(ScheduledTask).order_by(ScheduledTask.id.desc())
        if reduced:
            query = query.with_entities(ScheduledTask.id, ScheduledTask.created_at,ScheduledTask.name,ScheduledTask.user_id, ScheduledTask.description, ScheduledTask.enabled)

        if name is not None:
            query = query.filter(func.lower(ScheduledTask.name).like(func.lower(f"%{name}%")))
        if user_first_name is not None or user_last_name is not None:
            query = query.join(User, aliased=True)
            if user_first_name is not None:
                query = query.filter(func.lower(User.first_name).like(func.lower(f"%{user_first_name}%")))
            if user_last_name is not None:
                query = query.filter(func.lower(User.last_name).like(func.lower(f"%{user_last_name}%")))
        if start_condition_type is not None and start_condition_type != "":
            query = query.filter(ScheduledTask.start_condition_type == start_condition_type)
        if date_from is not None:
            query = query.filter(ScheduledTask.start_datetime >= date_from)
        if date_to is not None:
            query = query.filter(ScheduledTask.start_datetime <= date_to)
        if enabled is not None:
            query = query.filter(ScheduledTask.enabled == enabled)
        if frequency is not None:
            query = query.filter(ScheduledTask.frequency == frequency)
        if calibration_id is not None:
            query = query.filter(ScheduledTask.calibration_id == calibration_id)
        if calibration_id_for_simulations is not None:
            query = query.filter(ScheduledTask.calibration_id_for_simulations == calibration_id_for_simulations)
        return query.all()


def get_schedule_task_config(schedule_config_id) -> ScheduledTask:
    with get_session() as session:
        return (
            session.query(ScheduledTask)
            .filter(ScheduledTask.id == schedule_config_id)
            .first()
        )


def get_associated_execution_plans(scheduled_task_id):
    with get_session() as session:
        return (
            session.query(ExecutionPlanScheduleTaskMapping)
            .filter(ExecutionPlanScheduleTaskMapping.scheduled_task_id == scheduled_task_id)
            .all()
        )


def delete_scheduled_task(scheduled_task_id):
    try:
        scheduled_task = get_schedule_task_config(scheduled_task_id)
        if not scheduled_task:
            raise Exception(f"Scheduled task with id {scheduled_task_id} not found")
        execution_plan_schedule_task_mapping = get_associated_execution_plans(scheduled_task_id)

        for mapping in execution_plan_schedule_task_mapping:
            execution_plan_service.delete_execution_plan(mapping.execution_id)

        file_storage_service.delete_scheduled_task(scheduled_task_id)

        with get_session() as session:
            session.delete(scheduled_task)
            session.commit()

        return True
    except Exception as e:
        print("error while deleting scheduled task: " + scheduled_task_id)
        raise e


def copy_schedule_task(scheduled_task_id):
    s = get_schedule_task_config(scheduled_task_id)
    new_scheduled_task = create_copy(s.name, s.description, s.frequency, s.start_datetime,
                                     s.enabled, s.geometry_id, s.user_id, s.start_condition_type,
                                     s.observation_days, s.forecast_days, s.initial_flows,
                                     s.border_conditions, s.plan_series_list, s.calibration_id,
                                     s.calibration_id_for_simulations)
    file_storage_service.copy_execution_files_scheduled(scheduled_task_id, new_scheduled_task.id)
    return new_scheduled_task


def create_copy(name, description, frequency, start_datetime,
                enabled, geometry_id, user_id, start_condition_type,
                observation_days, forecast_days, initial_flows,
                border_conditions, plan_series_list, calibration_id,
                calibration_id_for_simulations):
    
    new_border_conditions = []
    for bc in border_conditions:
        new_bc = BorderCondition(
            scheduled_task_id = bc.scheduled_task_id,
            river = bc.river,
            reach = bc.reach,
            river_stat = bc.river_stat,
            interval = bc.interval,
            type = bc.type,
            series_id = bc.series_id
        )
        new_border_conditions.append(new_bc)


    new_plan_series_list = []
    for ps in plan_series_list:
        new_ps = PlanSeries(
            river = ps.river,
            reach = ps.reach,
            river_stat = ps.river_stat,
            stage_series_id = ps.stage_series_id,
            flow_series_id = ps.flow_series_id,
            scheduled_task_id = ps.scheduled_task_id,
            stage_datum = ps.stage_datum
        )
        new_plan_series_list.append(new_ps)


    with get_session() as session:
        scheduled_task = ScheduledTask(
            name=name,
            description=description,
            frequency=frequency,
            start_datetime=start_datetime,
            enabled=enabled,
            geometry_id=geometry_id,
            user_id=user_id,
            start_condition_type=start_condition_type,
            observation_days=observation_days,
            forecast_days=forecast_days,
            initial_flows=initial_flows,
            border_conditions=new_border_conditions,
            plan_series_list=new_plan_series_list,
            calibration_id=calibration_id,
            calibration_id_for_simulations=calibration_id_for_simulations
        )

        session.add(scheduled_task)
        session.commit()
        session.refresh(scheduled_task)

        return scheduled_task
