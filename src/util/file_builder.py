from io import BytesIO
from datetime import datetime
from string import Template


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
