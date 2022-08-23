from src.persistance.scheduled_task import ScheduledTask
from src.persistance.session import get_session
from src.service.user_service import get_current_user
from src.service.initial_flow_service import *
from src.service.border_series_service import *
from src.service.plan_series_service import *


def update(_id, form):
    with get_session() as session:
        schedule_config = session.query(ScheduledTask).filter_by(id=_id).one_or_none()
        schedule_config.frequency = form.frequency.data
        schedule_config.name = form.name.data
        schedule_config.description = form.description.data
        schedule_config.geometry_id = form.geometry_id.data
        schedule_config.start_datetime = form.start_datetime.data
        schedule_config.enabled = form.enabled.data
        schedule_config.observation_days = form.observation_days.data
        schedule_config.forecast_days = form.forecast_days.data
        schedule_config.start_condition_type = form.start_condition_type.data
        if form.start_condition_type.data == "restart_file":
            # TODO manejar logica para el restart file
            do = "something"
        update_initial_flows(session, _id, retrieve_initial_flows(form, _id))
        update_series_list(session, _id, retrieve_series(form, _id))
        update_plan_series_list(session, _id, retrieve_plan_series(form, _id))
        session.add(schedule_config)


def create(form):
    with get_session() as session:
        initial_flow_list = create_initial_flows(form)
        border_conditions = retrieve_series(form)
        plan_series_list = retrieve_plan_series(form)
        scheduled_task = ScheduledTask(
            frequency=form.frequency.data,
            enabled=form.enabled.data,
            name=form.name.data,
            description=form.description.data,
            geometry_id=form.geometry_id.data,
            start_datetime=form.start_datetime.data,
            start_condition_type=form.start_condition_type.data,
            observation_days=form.observation_days.data,
            forecast_days=form.forecast_days.data,
            user=get_current_user(),
            initial_flows=initial_flow_list,
            border_conditions=border_conditions,
            plan_series_list=plan_series_list,
        )
        session.add(scheduled_task)
        return scheduled_task


def get_schedule_tasks():
    with get_session() as session:
        return session.query(ScheduledTask).all()


def get_schedule_task_config(schedule_config_id):
    with get_session() as session:
        return (
            session.query(ScheduledTask)
            .filter(ScheduledTask.id == schedule_config_id)
            .first()
        )
