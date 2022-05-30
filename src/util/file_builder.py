from io import BytesIO
from string import Template
from src.parana.observations import obtain_observations
from src.parana.forecast import forecast
import more_itertools

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


def build_flow(start_date):
    # observations = obtain_observations()
    # data = forecast(observations)

    # Build .u
    with open("ina_resources/demo/condicion_de_borde.u01", "r+b") as f:
        return BytesIO(f.read())



class Flow:
    def __init__(self, river, reach, river_stat, interval, cond_borde, values, start_date):
        self.river = river
        self.reach = reach
        self.river_stat = river_stat
        self.interval = interval
        self.cond_borde = cond_borde
        self.values = values
        self.start_date = start_date

    def __str__(self):
        lines = []
        lines.append(f'Boundary Location={self.river},{self.reach},{self.river_stat},        ,                ,                ,                ,                ')
        lines.append(f'Interval={self.interval}')
        lines.append(f'{self.cond_borde}={len(self.values)}')
        lines += more_itertools.grouper([str(value).rjust(8, ' ') for value in self.values], 10)
        lines.append('DSS Path=')
        lines.append('Use DSS=False')
        lines.append('Use Fixed Start Time=True')
        lines.append(f'Fixed Start Date/Time={self.start_date},')
        lines.append('Is Critical Boundary=False')
        lines.append('Critical Boundary Flow=')

        return "\n".join(lines)

