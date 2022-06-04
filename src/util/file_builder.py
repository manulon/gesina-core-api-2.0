from io import BytesIO
from string import Template

from src.parana import entry_points, border_conditions_points, PARANA_ID
from src.parana.observations import obtain_observations
from src.parana.forecast import forecast
import more_itertools
from datetime import datetime, timedelta


def build_project(title, start_date, end_date):
    data = {
        "PROJECT_TITLE": title,
        "START_DATE": start_date.strftime("%d%b%Y"),
        "START_TIME": start_date.strftime("%H:%M"),
        "END_DATE": end_date.strftime("%d%b%Y"),
        "END_TIME": end_date.strftime("%H:%M"),
    }
    with open("src/file_templates/parana_prj_template.txt", "r") as f:
        src = Template(f.read())
    result = src.substitute(data)

    return BytesIO(result.encode("utf8"))


def build_plan(title, start_datetime, end_datetime):
    data = {
        "PLAN_TITLE": f"{title}-TRAZA",
        "PLAN_ID": f"{title}-TR",
        "TIMEFRAME": f'{start_datetime.strftime("%d%b%Y,%H:%M")},{end_datetime.strftime("%d%b%Y,%H:%M")}',
    }
    with open("src/file_templates/parana_plan_template.txt", "r") as f:
        src = Template(f.read())
    result = src.substitute(data)

    return BytesIO(result.encode("utf8"))


def build_flow(end_date=datetime(2022, 5, 18), days=60):
    end_date = (end_date + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_date = (end_date - timedelta(days=days)).replace(hour=0, minute=0, second=0)

    observations = obtain_observations(start_date, end_date)
    forecast_df, df_entry_points = forecast(observations)

    items = []

    items.append(
        Item(
            **entry_points[entry_points.river == "Parana"].iloc[0],
            start_date=start_date,
            values=observations[observations.Id_CB == PARANA_ID]["Nivel"],
        )
    )

    for entry_point in df_entry_points.columns:
        df = entry_points[entry_points.river == entry_point]
        if not df.empty:
            data = df.iloc[0].to_dict()
            items.append(
                Item(**data, start_date=start_date, values=df_entry_points[entry_point])
            )

    for point in forecast_df.columns:
        df = border_conditions_points[border_conditions_points.river == point]
        if not df.empty:
            data = df.iloc[0].to_dict()
            items.append(Item(**data, start_date=start_date, values=forecast_df[point]))

    # Build .u
    with open("src/file_templates/parana_flow_template.txt", "r") as f:
        src = Template(f.read())

    result = src.substitute({"ITEMS": "\n".join([str(i) for i in items])})

    return BytesIO(result.encode("utf8"))


class Item:
    def __init__(
        self, river, reach, river_stat, interval, border_condition, values, start_date
    ):
        self.river = river
        self.reach = reach
        self.river_stat = river_stat
        self.interval = interval
        self.border_condition = border_condition
        self.values = values
        self.start_date = start_date

    def __str__(self):
        lines = []
        lines.append(
            f"Boundary Location={self.river},{self.reach},{self.river_stat},        ,                ,                ,                ,                "
        )
        lines.append(f"Interval={self.interval}")
        lines.append(f"{self.border_condition}={len(self.values)}")
        groups = more_itertools.grouper(
            [str(value).rjust(8, " ") for value in self.values], 10, fillvalue=""
        )
        lines += ["".join(group) for group in groups]
        lines.append("DSS Path=")
        lines.append("Use DSS=False")
        lines.append("Use Fixed Start Time=True")
        lines.append(f'Fixed Start Date/Time={self.start_date.strftime("%d%b%Y")},')
        lines.append("Is Critical Boundary=False")
        lines.append("Critical Boundary Flow=")

        return "\n".join(lines)


if __name__ == "__main__":
    build_flow()
