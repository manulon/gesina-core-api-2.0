from src.persistance.scheduled_task import (
    ScheduledTask,
    InitialFlow,
    BorderCondition,
    BorderConditionType,
)
from src.persistance.session import get_session
from src.service.user_service import get_current_user


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
        initial_flow_list = (
            []
            if form.start_condition_type.data == "restart_file"
            else form.initial_flow_list
        )
        update_initial_flows(session, _id, initial_flow_list)
        update_series_list(session, _id, form.series_list)
        session.add(schedule_config)


def create(form):
    with get_session() as session:
        initial_flow_list = create_initial_flows(form)
        border_conditions = create_series_list(form.series_list)
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
        )
        session.add(scheduled_task)
        return scheduled_task


def create_initial_flows(form):
    list_from_form = (
        []
        if form.start_condition_type.data == "restart_file"
        else form.initial_flow_list
    )
    result = []
    for each_initial_flow in list_from_form:
        result.append(
            InitialFlow(
                river=each_initial_flow.river.data,
                reach=each_initial_flow.reach.data,
                river_stat=each_initial_flow.river_stat.data,
                flow=each_initial_flow.flow.data,
            )
        )
    return result


def update_initial_flows(session, scheduled_config_id, initial_flow_list):
    session.query(InitialFlow).filter_by(scheduled_task_id=scheduled_config_id).delete()
    for each_initial_flow in initial_flow_list:
        initial_flow = InitialFlow(
            scheduled_task_id=scheduled_config_id,
            river=each_initial_flow.river.data,
            reach=each_initial_flow.reach.data,
            river_stat=each_initial_flow.river_stat.data,
            flow=each_initial_flow.flow.data,
        )
        session.add(initial_flow)


def create_series_list(series_list):
    result = []
    for each_series in series_list:
        interval_data = each_series.interval.data
        interval = (
            str(interval_data["interval_value"]) + "-" + interval_data["interval_unit"]
        )
        result.append(
            BorderCondition(
                river=each_series.river.data,
                reach=each_series.reach.data,
                river_stat=each_series.river_stat.data,
                interval=interval,
                type=BorderConditionType(each_series.border_condition.data),
                observation_id=each_series.observation_id.data,
                forecast_id=each_series.forecast_id.data,
            )
        )

    return result


def update_series_list(session, scheduled_config_id, series_list):
    session.query(BorderCondition).filter_by(
        scheduled_task_id=scheduled_config_id
    ).delete()
    for each_series in series_list:
        interval_data = each_series.interval.data
        interval = (
            str(interval_data["interval_value"]) + "-" + interval_data["interval_unit"]
        )
        border_condition = BorderCondition(
            scheduled_task_id=scheduled_config_id,
            river=each_series.river.data,
            reach=each_series.reach.data,
            river_stat=each_series.river_stat.data,
            interval=interval,
            type=BorderConditionType(each_series.border_condition.data),
            observation_id=each_series.observation_id.data,
            forecast_id=each_series.forecast_id.data,
        )
        session.add(border_condition)


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


def get_complete_schedule_task_config(scheduled_config_id):
    with get_session() as session:
        return (
            session.query(ScheduledTask)
            .filter(ScheduledTask.id == scheduled_config_id)
            .first()
        )
