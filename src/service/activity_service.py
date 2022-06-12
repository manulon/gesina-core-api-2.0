import mpld3
from dateutil import rrule
from datetime import datetime, timedelta
import numpy as np
import random
import pandas

from matplotlib.figure import Figure

np.random.seed(19680801)


def execution_results():

    today = datetime.now()
    total_days = 30  # last month

    labels = []
    success_count = []
    error_count = []

    for day in rrule.rrule(
        rrule.DAILY,
        dtstart=today - timedelta(days=total_days + 1),
        until=today - timedelta(days=1),
    ):
        labels.append(day.date())
        success_count.append(random.randint(0, 50))
        error_count.append(random.randint(0, 25))

    width = 0.60
    fig = Figure(figsize=(6, 4))
    ax = fig.subplots()

    ax.bar(
        labels,
        success_count,
        width,
        label="Ok",
        color="green",
        edgecolor="black",
        align="edge",
    )
    ax.bar(
        labels,
        error_count,
        width,
        bottom=success_count,
        color="red",
        label="Error",
        edgecolor="black",
        align="edge",
    )

    ax.legend()

    return mpld3.fig_to_html(fig)


def execution_time_average():
    today = datetime.now()

    lista_de_corridas_con_fecha_y_tiempo = [
        ExecutionData(today),
        ExecutionData(today),
        ExecutionData(today - timedelta(days=1)),
        ExecutionData(today - timedelta(days=1)),
        ExecutionData(today - timedelta(days=1)),
        ExecutionData(today - timedelta(days=2)),
        ExecutionData(today - timedelta(days=2)),
        ExecutionData(today - timedelta(days=2)),
        ExecutionData(today - timedelta(days=3)),
        ExecutionData(today - timedelta(days=3)),
        ExecutionData(today - timedelta(days=3)),
        ExecutionData(today - timedelta(days=4)),
        ExecutionData(today - timedelta(days=5)),
    ]

    labels = []
    data = []

    for day in rrule.rrule(
        rrule.DAILY,
        dtstart=today - timedelta(days=5),
        until=today - timedelta(days=1),
    ):
        labels.append(day.date())

        executions_in_day = list(
            filter(
                lambda a: a.date.date() == day.date(),
                lista_de_corridas_con_fecha_y_tiempo,
            )
        )
        execution_time_list = list(map(lambda a: a.time_in_seconds, executions_in_day))
        average = 0
        if execution_time_list and execution_time_list > 0:
            average = sum(execution_time_list) / len(execution_time_list)
        data.append(average)

    fig = Figure(figsize=(6, 4))
    axs = fig.subplots()
    axs.plot(labels, data)
    axs.set_ylabel("Segundos")
    axs.grid(True)

    fig.tight_layout()
    return mpld3.fig_to_html(fig)


class ExecutionData:
    date = None
    time_in_seconds = None

    def __init__(self, date):
        self.date = date
        self.time_in_seconds = random.randint(400, 600)
