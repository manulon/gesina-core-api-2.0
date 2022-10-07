import io
from io import BytesIO
from string import Template

import numpy as np

from src.parana import entry_points, border_conditions_points, PARANA_ID
from src.parana.observations import obtain_observations
from src.parana.forecast import forecast
import more_itertools
from datetime import datetime, timedelta

from src.service import ina_service
from src.service import file_storage_service

TEMPLATES_DIR = "src/file_templates"
SCHEDULE_TASK_DIR = "scheduled-task"


def build_project(schedule_task_id, title, start_date, end_date):
    data = {
        "PROJECT_TITLE": title,
        "START_DATE": start_date.strftime("%d%b%Y"),
        "START_TIME": start_date.strftime("%H:%M"),
        "END_DATE": end_date.strftime("%d%b%Y"),
        "END_TIME": end_date.strftime("%H:%M"),
    }

    with file_storage_service.get_file(
        f"{SCHEDULE_TASK_DIR}/{schedule_task_id}/prj_template.txt"
    ) as template_file:
        decoded_file = BytesIO(template_file.data).read().decode("utf-8")
        src = Template(decoded_file)
        result = src.substitute(data)

    return BytesIO(result.encode("utf8"))


def build_plan(schedule_task_id, title, start_datetime, end_datetime):
    data = {
        "PLAN_TITLE": f"{title}-TRAZA",
        "PLAN_ID": f"{title}-TR",
        "TIMEFRAME": f'{start_datetime.strftime("%d%b%Y,%H:%M")},{end_datetime.strftime("%d%b%Y,%H:%M")}',
        "IC_TIME": f'{end_datetime.strftime("%d%b%Y,%H:%M")}',
    }
    with file_storage_service.get_file(
        f"{SCHEDULE_TASK_DIR}/{schedule_task_id}/plan_template.txt"
    ) as template_file:
        decoded_file = BytesIO(template_file.data).read().decode("utf-8")
        src = Template(decoded_file)
        result = src.substitute(data)

    return BytesIO(result.encode("utf8"))


def build_flow(
    end_date=datetime(2022, 5, 18), days=60, use_restart=False, initial_flows=None
):
    initial_status = create_initial_status(
        use_restart, "restart_file.rst", initial_flows
    )

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
    with io.open(f"{TEMPLATES_DIR}/unsteady_flow_template.txt", "r", newline="") as f:
        src = Template(f.read())

    result = src.substitute(
        {
            "INITIAL_STATUS": initial_status,
            "BOUNDARY_LOCATIONS": "\r\n".join([str(i) for i in items]),
        }
    )

    return BytesIO(result.encode("utf8"))


def create_initial_status(use_restart, restart_file, initial_flows):
    if use_restart:
        return build_restart_status(restart_file)
    return build_initial_flows(initial_flows)


def build_initial_flows(initial_flow_list):
    list_of_flows = []
    for initial_flow in initial_flow_list:
        list_of_flows.append(
            "Initial Flow Loc="
            + ",".join(
                [
                    str(initial_flow.river),
                    str(initial_flow.reach),
                    str(initial_flow.river_stat),
                    str(initial_flow.flow),
                ]
            )
        )
    initial_flows_string = "\r\n".join(list_of_flows)
    with io.open(f"{TEMPLATES_DIR}/initial_flows.txt", "r", newline="") as f:
        src = Template(f.read())
    return src.substitute({"INITIAL_FLOWS": initial_flows_string})


def build_restart_status(restart_filename):
    with io.open(f"{TEMPLATES_DIR}/restart_info.txt", "r", newline="") as f:
        src = Template(f.read())
    return src.substitute({"FILE_NAME": restart_filename})


def get_forecast_and_observation_values(border_conditions, start_date, end_date):
    result = []
    for condition in border_conditions:
        result.append(
            {
                "river": condition.river,
                "reach": condition.reach,
                "river_stat": condition.river_stat,
                "interval": condition.interval.replace("-", ""),
                "border_condition": condition.type,
                "values": ina_service.obtain_curated_series(
                    condition.observation_id, start_date, end_date
                ),
            }
        )
    return result


def build_boundary_conditions(start_date, conditions):
    boundary_locations = []
    with io.open(f"{TEMPLATES_DIR}/boundary_location.txt", "r", newline="") as f:
        src = Template(f.read())
        for condition in conditions:
            groups = more_itertools.grouper(
                [str(value).rjust(8, " ") for value in condition["values"]],
                10,
                fillvalue="",
            )

            condition_data = {
                "LOCATION": f"{condition['river']},{condition['reach']},{condition['river_stat']},        ,                ,                ,                ,                ",
                "INTERVAL": condition["interval"],
                "CONDITION_TYPE": condition["border_condition"],
                "AMOUNT": len(condition["values"]),
                "SERIES": "\r\n".join(["".join(group) for group in groups]),
                "START_DATE": start_date.strftime("%d%b%Y"),
            }
            boundary_locations.append(src.substitute(condition_data))
    return boundary_locations


def new_build_flow(
    border_conditions,
    use_restart,
    restart_file,
    initial_flows,
    start_date,
    end_date
):
    initial_status = create_initial_status(use_restart, restart_file, initial_flows)

    # Buscar las series al INA
    conditions = get_forecast_and_observation_values(
        border_conditions, start_date, end_date
    )
    boundary_locations = build_boundary_conditions(start_date, conditions)

    with io.open(f"{TEMPLATES_DIR}/unsteady_flow_template.txt", "r", newline="") as f:
        src = Template(f.read())
    result = src.substitute(
        {
            "INITIAL_STATUS": initial_status,
            "BOUNDARY_LOCATIONS": "".join(boundary_locations),
        }
    )

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
        self.values = [value if not np.isnan(value) else 1 for value in values]
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

        return "\r\n".join(lines)


if __name__ == "__main__":
    print(build_flow(use_restart=True).read().decode("utf8"))
