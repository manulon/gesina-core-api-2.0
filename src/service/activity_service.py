import base64
import io
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil import rrule
from matplotlib import cm
from src import config
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service.execution_plan_service import get_execution_plans_by_dates
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
    elif not date_from_param and date_to_param:
        date_to = datetime.strptime(date_to_param, "%d/%m/%Y").date()
        date_from = date_to - timedelta(weeks=1)
        if date_to > datetime.now().date():
            date_to = (datetime.now() - timedelta(days=1)).date()
    else:
        date_from = (datetime.now() - timedelta(weeks=1)).date()
        date_to = (datetime.now() - timedelta(days=1)).date()

    return date_from, date_to


def get_activity(date_from_param, date_to_param):
    plt.close("all")

    date_from, date_to = handle_activity_dates(date_from_param, date_to_param)

    executions = (
        get_execution_plans_by_dates(date_from, date_to)
        if not config.fake_activity
        else []
    )
    return execution_results(executions, date_from, date_to), execution_time_average(executions, date_from, date_to), contributions()


def _base_64_img(ax):
    img = io.BytesIO()
    ax.figure.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode("utf-8")


def execution_results(executions, date_from, date_to):
    if config.fake_activity:
        from src.service import fake_data_activity_service as fake_service

        return _base_64_img(fake_service.fake_execution_results())

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

        success_count.append(len(list(success_in_day)))
        error_count.append(len(list(error_in_day)))

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


def contributions():
    if config.fake_activity or True:
        from src.service import fake_data_activity_service as fake_service

        return _base_64_img(fake_service.fake_contributions())

    return None
    # En definitiva hay que tener una matriz de 7 x 30, donde los index son los días de la semana
    # today = datetime.now()
    # columns = []
    #
    # for week in rrule.rrule(
    #         rrule.WEEKLY,
    #         dtstart=today - timedelta(weeks=8),
    #         until=today - timedelta(days=1),
    # ):
    #     if day.date().weekday() == 0
    #     columns.append(day.date().strftime("%d/%m"))
    #
    # matrix = np.random.random((7, 31))
    # from src import logger
    # logger.error("matrix is " + str(matrix))
    # df = pandas.DataFrame(matrix,
    #                       index=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
    #                       columns=columns)
    # ax = seaborn.heatmap(df, cmap=seaborn.cm.rocket_r)
    # c_bar = ax.collections[0].colorbar
    # c_bar.ax.tick_params(labelsize=26)
    # return ax


def execution_time_average(executions, date_from, date_to):
    if config.fake_activity:
        from src.service import fake_data_activity_service as fake_service

        return _base_64_img(fake_service.fake_execution_time_average())

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

    fig, axs = plt.subplots(figsize=(25, 12.5))
    axs.plot(labels, data, c=cm.hot(0.25))
    axs.set_ylabel("Segundos", fontsize=30)
    axs.grid(True)

    plt.xticks(labels, rotation=65, fontsize=26)
    plt.yticks(fontsize=26)

    return _base_64_img(axs)
