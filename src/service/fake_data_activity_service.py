import matplotlib.pyplot as plt
import numpy as np
import random
from datetime import datetime, timedelta
from dateutil import rrule
from matplotlib import cm
import seaborn
import pandas

np.random.seed(19680801)


# FAKES
def fake_contributions():
    # En definitiva hay que tener una matriz de 7 x 30, donde los index son los días de la semana
    today = datetime.now()
    index = []
    for i in range(7):
        weekday = today.weekday()
        if weekday == 0:
            index.append('Lunes')
        elif weekday == 1:
            index.append('Martes')
        elif weekday == 2:
            index.append('Miercoles')
        elif weekday == 3:
            index.append('Jueves')
        elif weekday == 4:
            index.append('Viernes')
        elif weekday == 5:
            index.append('Sábado')
        elif weekday == 6:
            index.append('Domingo')

        today
    columns = []
    for day in rrule.rrule(
        rrule.WEEKLY,
        dtstart=today - timedelta(weeks=8),
        until=today - timedelta(days=1),
    ):
        from src import logger
        if
        logger.error("la week " + str(week))
        logger.error("la week " + str(week.weekday()))
        # columns.append(day.date().strftime("%d/%m"))

    matrix = np.random.random((7, 31))
    # logger.error("matrix is "+ str(matrix))
    df = pandas.DataFrame(matrix,
                          index=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    ax = seaborn.heatmap(df, cmap=seaborn.cm.rocket_r)
    c_bar = ax.collections[0].colorbar
    c_bar.ax.tick_params(labelsize=26)
    return ax


def fake_execution_results():
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
        labels.append(day.date().strftime("%d-%m"))
        success_count.append(random.randint(0, 50))
        error_count.append(random.randint(0, 5))

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

    return ax


def fake_execution_time_average():
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
        labels.append(day.date().strftime("%d-%m"))

        executions_in_day = list(
            filter(
                lambda a: a.date.date() == day.date(),
                lista_de_corridas_con_fecha_y_tiempo,
            )
        )
        execution_time_list = list(map(lambda a: a.time_in_seconds, executions_in_day))
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

    return axs


class ExecutionData:
    date = None
    time_in_seconds = None

    def __init__(self, date):
        self.date = date
        self.time_in_seconds = random.randint(400, 600)
