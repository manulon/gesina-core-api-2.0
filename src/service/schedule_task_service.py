from src.persistance.scheduled_task import ScheduledTask
from src.persistance.session import get_session
from src.service import project_file_service, plan_file_service, file_storage_service
from src.service.file_storage_service import save_restart_file, FileType
from src.service.user_service import get_current_user
from src.service.initial_flow_service import *
from src.service.border_series_service import *
from src.service.plan_series_service import *

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
        schedule_config.enabled = form.enabled.data
        schedule_config.observation_days = form.observation_days.data
        schedule_config.forecast_days = form.forecast_days.data
        schedule_config.start_condition_type = form.start_condition_type.data
        update_series_list(session, _id, retrieve_series(form, _id))
        update_plan_series_list(session, _id, retrieve_plan_series(form, _id))

        if form.start_condition_type.data == "restart_file" and form.restart_file.data:
            save_restart_file(form.restart_file.data, schedule_config.id)
        else:
            update_initial_flows(session, _id, retrieve_initial_flows(form, _id))

        project_file_service.process_project_template(form.project_file.data, _id)
        plan_file_service.process_plan_template(form.plan_file.data, _id)
        session.add(schedule_config)

def create(form):
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
        "border_conditions": retrieve_series(form),
        "plan_series_list": retrieve_plan_series(form),
    }

    if form.start_condition_type.data == "initial_flows":
        params["initial_flows"] = create_initial_flows(form)

    with get_session() as session:
        scheduled_task = ScheduledTask(**params)
        session.add(scheduled_task)

        session.commit()
        session.refresh(scheduled_task)
        if form.start_condition_type.data == "restart_file":
            save_restart_file(form.restart_file.data, scheduled_task.id)

        project_file_service.process_project_template(
            form.project_file.data, scheduled_task.id
        )
        plan_file_service.process_plan_template(form.plan_file.data, scheduled_task.id)

        return scheduled_task

def get_schedule_tasks():
    with get_session() as session:
        return session.query(ScheduledTask).order_by(ScheduledTask.id.desc()).all()

def get_schedule_task_config(schedule_config_id):
    with get_session() as session:
        return (
            session.query(ScheduledTask)
            .filter(ScheduledTask.id == schedule_config_id)
            .first()
        )

def delete_scheduled_task(scheduled_task_id):
    try:
        scheduled_task = get_schedule_task_config(scheduled_task_id)

        file_storage_service.delete_scheduled_task(scheduled_task_id)

        # - Esto tira una excepcion. -
        with get_session() as session:
            session.delete(scheduled_task)
            session.commit()
        return True
    except Exception as e:
        print("error while deleting scheduled task: " + scheduled_task_id)
        print(e)
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
    with get_session() as session:
        scheduled_task = ScheduledTask(
            name = name, 
            description = description,
            frequency = frequency,
            start_datetime = start_datetime,
            enabled = enabled,
            geometry_id = geometry_id,
            user_id = user_id,
            start_condition_type = start_condition_type,
            observation_days = observation_days,
            forecast_days = forecast_days,
            initial_flows = initial_flows,
            border_conditions = border_conditions,
            plan_series_list = plan_series_list,
            calibration_id = calibration_id,
            calibration_id_for_simulations = calibration_id_for_simulations
        )
        
        session.add(scheduled_task)
        session.commit()
        session.refresh(scheduled_task)
        
        return scheduled_task