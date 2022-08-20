from src.persistance.scheduled_task import (
    ScheduledTask,
    InitialFlow,
    BorderCondition,
    BorderConditionType,
    PlanSeries,
)
from src.persistance.session import get_session
from src.service.exception.file_exception import FileUploadError
from src.service.user_service import get_current_user


def process_form(scheduled_config_id, initial_flow_list):
    result = []
    for each_initial_flow in initial_flow_list:
        initial_flow = InitialFlow(
            scheduled_task_id=scheduled_config_id,
            river=each_initial_flow.river.data,
            reach=each_initial_flow.reach.data,
            river_stat=each_initial_flow.river_stat.data,
            flow=each_initial_flow.flow.data,
        )
        result.append(initial_flow)
    return result


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
        else:
            from_csv = process_csv_file(_id, form.initial_flow_file)
            from_form = process_form(_id, form.initial_flow_list)
        update_initial_flows(session, _id, from_csv + from_form)
        update_series_list(session, _id, form.series_list)
        update_plan_series_list(session, _id, form.plan_series_list)
        session.add(schedule_config)


def create(form):
    with get_session() as session:
        initial_flow_list = create_initial_flows(form)
        border_conditions = create_series_list(form.series_list)
        plan_series_list = create_plan_series_list(form.plan_series_list)
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


def process_csv_file(scheduled_config_id, initial_flow_file_field):
    import csv
    import io

    result = []
    if initial_flow_file_field.data:
        buffer = initial_flow_file_field.data.read()
        content = buffer.decode()
        file = io.StringIO(content)
        csv_data = csv.reader(file, delimiter=",")
        header = next(csv_data)
        if (
            len(header) == 4
            and header[0] == "river"
            and header[1] == "reach"
            and header[2] == "river_stat"
            and header[3] == "flow"
        ):
            for row in csv_data:
                initial_flow = InitialFlow(
                    scheduled_task_id=scheduled_config_id,
                    river=row[0],
                    reach=row[1],
                    river_stat=row[2],
                    flow=row[3],
                )
                result.append(initial_flow)
        else:
            raise FileUploadError("Error: Archivo .csv inválido")

    return result


def create_initial_flows(form):
    if form.start_condition_type.data == "restart_file":
        list_from_form = process_csv_file(form.restart_file)
    else:
        list_from_form = form.initial_flow_list

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


def update_initial_flows(session, scheduled_config_id, initial_flows):
    session.query(InitialFlow).filter_by(scheduled_task_id=scheduled_config_id).delete()
    for each_initial_flow in initial_flows:
        session.add(each_initial_flow)


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


def create_plan_series_list(plan_series_list):
    return [
        PlanSeries(
            river=plan_series.river,
            reach=plan_series.reach,
            river_stat=plan_series.river_stat,
            series_id=plan_series.series_id,
        )
        for plan_series in plan_series_list
    ]


def update_plan_series_list(session, scheduled_config_id, plan_series_list):
    session.query(PlanSeries).filter(
        PlanSeries.scheduled_task_id == scheduled_config_id
    ).filter(
        PlanSeries.id.not_in({p.idx.data for p in plan_series_list if p.idx.data}),
    ).delete()
    for series in plan_series_list:
        if series.idx.data:
            plan_series = (
                session.query(PlanSeries)
                .filter(PlanSeries.id == series.idx.data)
                .first()
            )
            plan_series.river = series.river.data
            plan_series.reach = series.reach.data
            plan_series.river_stat = series.river_stat.data
            plan_series.series_id = series.series_id.data
        else:
            plan_series = PlanSeries(
                scheduled_task_id=scheduled_config_id,
                river=series.river.data,
                reach=series.reach.data,
                river_stat=series.river_stat.data,
                series_id=series.series_id.data,
            )
            session.add(plan_series)


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
