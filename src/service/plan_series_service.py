import csv
import io
from src.persistance.scheduled_task import (
    BorderCondition,
    PlanSeries,
)
from src.service.exception.file_exception import FileUploadError

CSV_HEADERS = ["river", "reach", "river_stat", "series_id"]


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
                series_id=each_plan_series.series_id.data,
            )
        else:
            plan_series = BorderCondition(
                river=each_plan_series.river.data,
                reach=each_plan_series.reach.data,
                river_stat=each_plan_series.river_stat.data,
                series_id=each_plan_series.series_id.data,
            )
        result.append(plan_series)

    return result


def process_plan_series_csv_file(plan_series_file_field, scheduled_config_id=None):
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
                        series_id=row[3],
                    )
                else:
                    plan_series = PlanSeries(
                        river=row[0], reach=row[1], river_stat=row[2], series_id=row[3]
                    )
                result.append(plan_series)
        else:
            raise FileUploadError("Error: Archivo .csv inválido")

    return result


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
