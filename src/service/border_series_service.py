import csv
import io
import re as regex
from pytz import utc, timezone
from datetime import datetime
from datetime import timedelta
from src import config
import requests

from src.persistance.scheduled_task import (
    BorderCondition,
    BorderConditionType, ScheduledTask,
)
from src.persistance.session import get_session
from src.service import file_storage_service
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
    from_csv = process_series_csv_file(form.series_list_file.data, scheduled_config_id)
    from_form = process_series_form(form.series_list, scheduled_config_id)
    merged_series = from_csv + from_form
    for series in merged_series:
        if not bool(regex.match(SERIES_INTERVAL_REGEX, series.interval)):
            raise SeriesUploadError("Error: Interval con formato incorrecto")
    return merged_series


def retrieve_series_json(series_list_file, series_list, scheduled_config_id=None):
    from_csv = process_series_csv_file(
        None if series_list_file == None else file_storage_service.get_file(series_list_file))
    from_json = process_series_json(series_list, scheduled_config_id)
    merged_series = from_csv + from_json
    for series in merged_series:
        if not bool(regex.match(SERIES_INTERVAL_REGEX, series.interval)):
            raise SeriesUploadError("Error: Interval con formato incorrecto")
    return merged_series


def add_series_to_scheduled_task(oneSeries, scheduled_config_id):
    if not scheduled_config_id:
        raise Exception("Scheduled config id not present while adding new border series")
    seriesList = process_series_json([oneSeries],scheduled_config_id)
    with get_session() as session:
        session.add(seriesList[0])



def update_series_list(session, scheduled_config_id, series):
    session.query(BorderCondition).filter_by(
        scheduled_task_id=scheduled_config_id
    ).delete()
    for each_series in series:
        session.add(each_series)


def update_border_condition(condition, new_condition):
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


def process_series_csv_file(series_file, scheduled_config_id=None):
    result = []
    if series_file:
        buffer = series_file.read()
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
                        type=BorderConditionType(row[4]),
                        series_id=row[5],
                    )
                else:
                    border_condition = BorderCondition(
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        interval=row[3],
                        type=BorderConditionType(row[4]),
                        series_id=row[5],
                    )
                result.append(border_condition)
        else:
            raise FileUploadError("Error: Archivo .csv inválido - Border series service")

    if series_file is not None:
            series_file.seek(0)
    return result


def forecast_and_observation_values_exists(form):
    locale = timezone("America/Argentina/Buenos_Aires")
    today = datetime.now(tz=locale).replace(minute=0)
    start_date = today - timedelta(form.observation_days.data)
    end_date = today + timedelta(form.forecast_days.data)

    format_time = lambda d: d.strftime("%Y-%m-%d")
    timestart = start_date - timedelta(1)
    timeend = end_date + timedelta(1)

    border_conditions = retrieve_series(form)

    if len(border_conditions) > 0:
        url = f"{config.ina_url}/sim/calibrados/{form.calibration_id.data}/corridas/last?series_id={border_conditions[0].series_id}&timestart={format_time(timestart)}&timeend={format_time(timeend)}"

        response = None
        for i in range(config.max_retries):
            response = requests.get(
                url, headers={"Authorization": f"Bearer {config.ina_token}"}
            )
            if response.status_code == 200 and len(response.json()["series"]) > 0:
                return True, border_conditions
            else:
                return False, None
    else:
        empty_list = []
        return False, empty_list

    return False, None


def forecast_and_observation_values_exists_json(border_conditions, observation_days, forecast_days, calibration_id):
    locale = timezone("America/Argentina/Buenos_Aires")
    today = datetime.now(tz=locale).replace(minute=0)
    start_date = today - timedelta(observation_days)
    end_date = today + timedelta(forecast_days)

    format_time = lambda d: d.strftime("%Y-%m-%d")
    timestart = start_date - timedelta(1)
    timeend = end_date + timedelta(1)

    if len(border_conditions) > 0:
        if str(type(border_conditions[0])).__contains__("BorderCondition") :
            series_id = border_conditions[0].series_id
        else:
            series_id = border_conditions[0].get("series_id")
        url = f"{config.ina_url}/sim/calibrados/{calibration_id}/corridas/last?series_id={series_id}&timestart={format_time(timestart)}&timeend={format_time(timeend)}"
        response = None
        for i in range(config.max_retries):
            response = requests.get(
                url, headers={"Authorization": f"Bearer {config.ina_token}"}
            )
            if response.status_code == 200 and len(response.json()["series"]) > 0:
                return True
            else:
                return False

    return False
