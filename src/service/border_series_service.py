import csv
import io
import re as regex
from src.persistance.scheduled_task import (
    BorderCondition,
    BorderConditionType,
)
from src.service.exception.file_exception import FileUploadError
from src.service.exception.series_exception import SeriesUploadError

SERIES_INTERVAL_REGEX = "^[0-9]*-(MINUTE|HOUR|DAY|WEEK)$"

BORDER_SERIES_CSV_HEADERS = [
    "river",
    "reach",
    "river_stat",
    "interval",
    "type",
    "series_id",
]

def retrieve_series(form, scheduled_config_id=None):
    from_csv = process_series_csv_file(form.series_list_file, scheduled_config_id)
    from_form = process_series_form(form.series_list, scheduled_config_id)
    merged_series = from_csv + from_form
    for series in merged_series:
        if not bool(regex.match(SERIES_INTERVAL_REGEX, series.interval)):
            raise SeriesUploadError("Error: Interval con formato incorrecto")
    return merged_series

def update_series_list(session, scheduled_config_id, series):
    session.query(BorderCondition).filter_by(
        scheduled_task_id=scheduled_config_id
    ).delete()
    for each_series in series:
        session.add(each_series)

def update_border_condition(condition, new_condition):
    #TODO validate values
    for key, value in new_condition.items():
        if key in BORDER_SERIES_CSV_HEADERS:
            setattr(condition, key, value)

def process_series_form(series_list, scheduled_config_id=None):
    result = []
    for each_series in series_list:
        interval_data = each_series.interval.data
        interval = (
            str(interval_data["interval_value"]) + "-" + interval_data["interval_unit"]
        )
        if scheduled_config_id:
            border_condition = BorderCondition(
                scheduled_task_id=scheduled_config_id,
                river=each_series.river.data,
                reach=each_series.reach.data,
                river_stat=each_series.river_stat.data,
                interval=interval,
                type=BorderConditionType(each_series.border_condition.data),
                series_id=each_series.series_id.data,
            )
        else:
            border_condition = BorderCondition(
                river=each_series.river.data,
                reach=each_series.reach.data,
                river_stat=each_series.river_stat.data,
                interval=interval,
                type=BorderConditionType(each_series.border_condition.data),
                series_id=each_series.series_id.data,
            )
        result.append(border_condition)

    return result

def process_series_json(series_list, scheduled_config_id=None):
    result = []
    for each_series in series_list:
        interval = each_series.get("interval")
        if scheduled_config_id:
            border_condition = BorderCondition(
                scheduled_task_id=scheduled_config_id,
                river=each_series.get("river"),
                reach=each_series.get("reach"),
                river_stat=each_series.get("river_stat"),
                interval=interval,
                type=BorderConditionType(each_series.get("type")),
                series_id=each_series.get("series_id"),
            )
        else:
            border_condition = BorderCondition(
                river=each_series.get("river"),
                reach=each_series.get("reach"),
                river_stat=each_series.get("river_stat"),
                interval=interval,
                type=BorderConditionType(each_series.get("type")),
                series_id=each_series.get("series_id"),
            )
        result.append(border_condition)

    return result


def process_series_csv_file(series_file_field, scheduled_config_id=None):
    result = []
    if series_file_field.data:
        buffer = series_file_field.data.read()
        content = buffer.decode()
        file = io.StringIO(content)
        csv_data = csv.reader(file, delimiter=",")
        header = next(csv_data)
        if len(header) >= 6 and header[:6] == BORDER_SERIES_CSV_HEADERS:
            for row in csv_data:
                if scheduled_config_id:
                    border_condition = BorderCondition(
                        scheduled_task_id=scheduled_config_id,
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        interval=row[3],
                        type=row[4],
                        series_id=row[5],
                    )
                else:
                    border_condition = BorderCondition(
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        interval=row[3],
                        type=row[4],
                        series_id=row[5],
                    )
                result.append(border_condition)
        else:
            raise FileUploadError("Error: Archivo .csv inválido - Border series service")

    return result
