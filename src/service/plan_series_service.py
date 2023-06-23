import csv
import io
from src.persistance.scheduled_task import (
    BorderCondition,
    PlanSeries,
)
from src.service.exception.file_exception import FileUploadError

CSV_HEADERS = ["river", "reach", "river_stat", "stage_series_id", "flow_series_id", "stage_datum"]


def retrieve_plan_series(form, scheduled_config_id=None):
    from_csv = process_plan_series_csv_file(form.plan_series_file, scheduled_config_id)
    from_form = process_plan_series_form(form.plan_series_list, scheduled_config_id)
    return from_csv + from_form


def update_plan_series_list(session, scheduled_config_id, plan_series_list):
    session.query(PlanSeries).filter_by(scheduled_task_id=scheduled_config_id).delete()
    for plan_series in plan_series_list:
        session.add(plan_series)


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


def process_plan_series_csv_file(plan_series_file_field, scheduled_config_id=None):
    print("<<<<<<<<<<<<<< Import PLAN SERIES CSV >>>>>>>>>>>>>>>>>>>")
    result = []
    if plan_series_file_field.data:
        buffer = plan_series_file_field.data.read()
        content = buffer.decode()
        file = io.StringIO(content)
        csv_data = csv.reader(file, delimiter=",")
        header = next(csv_data)
        if header == CSV_HEADERS:
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
            raise FileUploadError("Error: Archivo .csv inválido")

    return result
