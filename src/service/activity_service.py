import base64
import io
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil import rrule
from matplotlib import cm
import seaborn
import pandas
import numpy as np
from src import config
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service.execution_plan_service import (
    get_execution_plans_by_dates,
    get_execution_plans_grouped_by_interval,
)
from src.service.exception.activity_exception import (
    ActivityInvalidDates,
    ActivityMaxDaysReached,
)


def handle_activity_dates(date_from_param, date_to_param):
    if date_from_param and date_to_param:
        date_from = datetime.strptime(date_from_param, "%d/%m/%Y").date()
        date_to = datetime.strptime(date_to_param, "%d/%m/%Y").date()
        if date_from > date_to:
            raise ActivityInvalidDates("Fecha desde no puede ser mayor a fecha hasta.")
        if (date_to - date_from).days > 30:
            raise ActivityMaxDaysReached("La longitud máxima de días es de 30")
    elif date_from_param and not date_to_param:
        date_from = datetime.strptime(date_from_param, "%d/%m/%Y").date()
        date_to = date_from + timedelta(weeks=1)
        date_to = (datetime.now() + timedelta(days=1)).date() if date_to > datetime.now().date() else date_to
    elif not date_from_param and date_to_param:
        date_to = datetime.strptime(date_to_param, "%d/%m/%Y").date()
        date_from = date_to - timedelta(weeks=1)
        if date_to > datetime.now().date():
            date_to = (datetime.now() - timedelta(days=1)).date()
    else:
        date_from = (datetime.now() - timedelta(weeks=1)).date()
        date_to = (datetime.now() - timedelta(days=1)).date()

    return date_from, date_to


def get_activity(activity_params):
    plt.close("all")

    date_from, date_to = handle_activity_dates(
        activity_params.get("date_from"), activity_params.get("date_to")
    )

    executions = (
        get_execution_plans_by_dates(date_from, date_to)
        if not config.fake_activity
        else []
    )
    return (
        execution_results(executions, date_from, date_to),
        execution_time_average(executions, date_from, date_to),
        contributions(),
    )


def execution_results_data(executions, date_from, date_to):
    labels = []
    success_count = []
    error_count = []
    for day in rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to):
        labels.append(day.date().strftime("%d-%m"))

        success_in_day = filter(
            lambda ex: ex.created_at.date() == day.date()
                       and ex.status == ExecutionPlanStatus.FINISHED,
            executions,
        )
        error_in_day = filter(
            lambda ex: ex.created_at.date() == day.date()
                       and ex.status == ExecutionPlanStatus.ERROR,
            executions,
        )

        success_count.append(list(success_in_day).__len__())
        error_count.append(list(error_in_day).__len__())
    return labels, success_count, error_count


def _base_64_img(ax):
    img = io.BytesIO()
    ax.figure.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode("utf-8")


def execution_results(executions, date_from, date_to):
    if config.fake_activity:
        from src.service import fake_data_activity_service as fake_service

        return _base_64_img(fake_service.fake_execution_results())
    labels, success_count, error_count = execution_results_data(executions, date_from, date_to)

    width = 0.60
    fig, ax = plt.subplots(figsize=(25, 12))

    ax.bar(
        labels,
        success_count,
        width,
        label="Ok",
        color="#298f37",
        edgecolor="#113f0c",
        align="edge",
    )
    ax.bar(
        labels,
        error_count,
        width,
        bottom=success_count,
        color="#f0604d",
        label="Error",
        edgecolor="#8f3229",
        align="edge",
    )
    plt.xticks(labels, rotation=65, fontsize=26)
    plt.yticks(fontsize=26)
    plt.legend(fontsize=26)

    return _base_64_img(ax)


def get_first_sunday_date(today):
    three_months_ago = today - timedelta(weeks=12)
    return three_months_ago + timedelta(days=6 - three_months_ago.weekday())


def contributions():
    if config.fake_activity:
        from src.service import fake_data_activity_service as fake_service

        return _base_64_img(fake_service.fake_contributions())

    today = datetime.combine(datetime.now(), datetime.min.time())
    index = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

    columns = []
    matrix = np.zeros((7, 12))
    result = list(get_execution_plans_grouped_by_interval("3 months"))

    first_sunday_date = get_first_sunday_date(today)
    i = 0
    j = 0
    for day in rrule.rrule(
            rrule.DAILY,
            dtstart=first_sunday_date + timedelta(days=1),
            until=first_sunday_date + timedelta(weeks=12),
    ):
        if j == 0:
            sunday_of_the_week = day + timedelta(days=6)
            columns.append(
                day.strftime("%d/%m") + "-" + sunday_of_the_week.strftime("%d/%m")
            )

        results_for_day = list(
            filter(
                lambda row: datetime(int(row[3]), int(row[2]), int(row[1])).date()
                            == day.date(),
                result,
            )
        )
        quantity = 0
        if results_for_day:
            quantity = results_for_day[0][0]

        matrix[j, i] = quantity
        j = j + 1
        if j == 7:
            j = 0
            i = i + 1

    df = pandas.DataFrame(data=matrix, index=index, columns=columns)
    ax = seaborn.heatmap(df, cmap=seaborn.cm._lut)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=20, rotation=65)
    c_bar = ax.collections[0].colorbar
    c_bar.ax.tick_params(labelsize=26)

    return _base_64_img(ax)


def execution_time_average_data(executions, date_from, date_to):
    labels = []
    data = []
    for day in rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to):
        labels.append(day.date().strftime("%d-%m"))

        executions_in_day = list(
            filter(
                lambda ex: ex.created_at.date() == day.date(),
                executions,
            )
        )
        execution_time_list = list(
            map(
                lambda execution: (
                        execution.end_datetime - execution.start_datetime
                ).total_seconds(),
                executions_in_day,
            )
        )
        average = 0
        if execution_time_list:
            average = sum(execution_time_list) / len(execution_time_list)
        data.append(average)
    return labels, data


def execution_time_average(executions, date_from, date_to):
    if config.fake_activity:
        from src.service import fake_data_activity_service as fake_service

        return _base_64_img(fake_service.fake_execution_time_average())

    labels, data = execution_time_average_data(executions, date_from, date_to)

    fig, axs = plt.subplots(figsize=(25, 12.5))
    axs.plot(labels, data, c=cm.hot(0.25))
    axs.set_ylabel("Segundos", fontsize=30)
    axs.grid(True)

    plt.xticks(labels, rotation=65, fontsize=26)
    plt.yticks(fontsize=26)

    return _base_64_img(axs)


def get_activity_data(date_from=None, date_to=None):
    date_from, date_to = handle_activity_dates(date_from, date_to)
    executions = (
        get_execution_plans_by_dates(date_from, date_to)
        if not config.fake_activity
        else []
    )
    return execution_results_data(executions, date_from, date_to)


def get_execution_average_time_data(date_from=None, date_to=None):
    date_from, date_to = handle_activity_dates(date_from, date_to)
    executions = (
        get_execution_plans_by_dates(date_from, date_to)
        if not config.fake_activity
        else []
    )
    return execution_time_average_data(executions, date_from, date_to)
