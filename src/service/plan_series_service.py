import csv
import io

from src.controller.schemas import PLAN_SERIES_SCHEMA
from src.persistance.scheduled_task import (
    BorderCondition,
    PlanSeries, ScheduledTask,
)
from src.persistance.session import get_session
from src.service import file_storage_service
from src.service.exception.file_exception import FileUploadError

PLAN_SERIES_CSV_HEADERS = ["river", "reach", "river_stat", "stage_series_id", "flow_series_id", "stage_datum"]


def retrieve_plan_series(form, scheduled_config_id=None):
    from_csv = process_plan_series_csv_file(form.plan_series_file.data, scheduled_config_id)
    from_form = process_plan_series_form(form.plan_series_list, scheduled_config_id)
    return from_csv + from_form


def retrieve_plan_series_json(plan_series_file, plan_series_list, scheduled_config_id=None):
    from_csv = process_plan_series_csv_file(None if plan_series_file == None else
                                            file_storage_service.get_file(plan_series_file), scheduled_config_id)
    from_json = process_plan_series_json(plan_series_list, scheduled_config_id)
    return from_csv + from_json


def update_plan_series_list(session, scheduled_config_id, plan_series_list):
    session.query(PlanSeries).filter_by(scheduled_task_id=scheduled_config_id).delete()
    for plan_series in plan_series_list:
        session.add(plan_series)


def update_plan_series(plan, new_plan):
    # TODO validate values
    for key, value in new_plan.items():
        if key in PLAN_SERIES_CSV_HEADERS:
            setattr(plan, key, value)


def process_plan_series_form(series_list, scheduled_config_id=None):
    result = []
    for each_plan_series in series_list:
        if scheduled_config_id:
            plan_series = PlanSeries(
                scheduled_task_id=scheduled_config_id,
                river=each_plan_series.river.data,
                reach=each_plan_series.reach.data,
                river_stat=each_plan_series.river_stat.data,
                stage_series_id=each_plan_series.stage_series_id.data,
                flow_series_id=each_plan_series.flow_series_id.data,
                stage_datum=each_plan_series.stage_datum.data
            )
        else:
            plan_series = PlanSeries(
                river=each_plan_series.river.data,
                reach=each_plan_series.reach.data,
                river_stat=each_plan_series.river_stat.data,
                stage_series_id=each_plan_series.stage_series_id.data,
                flow_series_id=each_plan_series.flow_series_id.data,
                stage_datum=each_plan_series.stage_datum.data
            )
        result.append(plan_series)

    return result


def process_plan_series_json(series_list, scheduled_config_id=None):
    result = []
    for each_plan_series in series_list:
        if scheduled_config_id:
            plan_series = PlanSeries(
                scheduled_task_id=scheduled_config_id,
                river=each_plan_series.get("river"),
                reach=each_plan_series.get("reach"),
                river_stat=each_plan_series.get("river_stat"),
                stage_series_id=each_plan_series.get("stage_series_id"),
                flow_series_id=each_plan_series.get("flow_series_id"),
                stage_datum=each_plan_series.get("stage_datum")
            )
        else:
            plan_series = PlanSeries(
                river=each_plan_series.get("river"),
                reach=each_plan_series.get("reach"),
                river_stat=each_plan_series.get("river_stat"),
                stage_series_id=each_plan_series.get("stage_series_id"),
                flow_series_id=each_plan_series.get("flow_series_id"),
                stage_datum=each_plan_series.get("stage_datum")
            )
        result.append(plan_series)

    return result


def process_plan_series_csv_file(plan_series_file, scheduled_config_id=None):
    result = []
    if plan_series_file:
        buffer = plan_series_file.read()
        content = buffer.decode()
        file = io.StringIO(content)
        csv_data = csv.reader(file, delimiter=",")
        header = next(csv_data)
        if len(header) >= 5 and header == PLAN_SERIES_CSV_HEADERS:
            for row in csv_data:
                if scheduled_config_id:
                    plan_series = PlanSeries(
                        scheduled_task_id=scheduled_config_id,
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        stage_series_id=row[3],
                        flow_series_id=row[4],
                        stage_datum=row[5] if len(row[5]) else None
                    )
                else:
                    plan_series = PlanSeries(
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        stage_series_id=row[3],
                        flow_series_id=row[4],
                        stage_datum=row[5] if len(row[5]) else None
                    )
                result.append(plan_series)
        else:
            raise FileUploadError("Error: Archivo .csv inválido - Plan series service")
    if plan_series_file is not None:
        plan_series_file.seek(0)
    return result


def check_duplicate_output_series(form):
    plan_series = retrieve_plan_series(form)

    dict_plan_series = {}

    for var in plan_series:
        if (var.river, var.reach, var.river_stat) in dict_plan_series:
            return True, plan_series, (var.river, var.reach, var.river_stat)
        else:
            dict_plan_series[(var.river, var.reach, var.river_stat)] = 'value'
    return False, plan_series, None


def check_duplicate_output_series_json(plan_series, schedule_config: ScheduledTask = None):
    dict_plan_series = {}
    if schedule_config:
        for var in schedule_config.plan_series_list:
            dict_plan_series[(var.river, var.reach, var.river_stat)] = 'value'

    if not plan_series:
        return False, None
    if str(type(plan_series[0])).__contains__("PlanSeries"):
        plan_series = PLAN_SERIES_SCHEMA.dump(plan_series,many=True)
    for var in plan_series:
        if (var.get("river"), var.get("reach"), var.get("river_stat")) in dict_plan_series:
            return True, (var.get("river"), var.get("reach"), var.get("river_stat"))
        else:
            dict_plan_series[(var.get("river"), var.get("reach"), var.get("river_stat"))] = 'value'

    return False, None


def add_series_to_scheduled_task(oneSeries, scheduled_config_id):
    if not scheduled_config_id:
        raise Exception("Scheduled config id not present while adding new border series")
    seriesList = process_plan_series_json([oneSeries], scheduled_config_id)
    with get_session() as session:
        session.add(seriesList[0])
