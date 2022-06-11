import mpld3
from dateutil import rrule
from datetime import datetime, timedelta

from matplotlib.figure import Figure


def execution_results():
    import random

    today = datetime.now()
    total_days = 30  # last month

    activity_days = []
    labels = []
    success_count = []
    error_count = []

    random.seed(1)
    for day in rrule.rrule(
        rrule.DAILY,
        dtstart=today - timedelta(days=total_days + 1),
        until=today - timedelta(days=1),
    ):
        activity_days.append(day)
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
