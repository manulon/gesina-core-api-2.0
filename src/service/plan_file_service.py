import io

from src.service import file_storage_service

LINES_TO_PROCESS = [
    "Plan Title",
    "Short Identifier",
    "Simulation Date",
    "Geom File",
    "Flow File",
]

LINES_CHANGES = {
    "Plan Title": "Plan Title=$PLAN_TITLE",
    "Short Identifier": "Short Identifier=$PLAN_ID",
    "Simulation Date": "Simulation Date=$TIMEFRAME",
    "Geom File": "Geom File=g01",
    "Flow File": "Flow File=u01",
}


def process_plan_template(plan_file, schedule_task_id):
    if plan_file:
        content = ""
        decoded_file = plan_file.read().decode("utf-8")

        for line in decoded_file.splitlines():
            line_to_change = next(
                filter(lambda each_line: each_line in line, LINES_TO_PROCESS), None
            )
            if line_to_change:
                content += LINES_CHANGES.get(line_to_change)
            else:
                content += line
            content += "\r\n"

        result_file = io.BytesIO(bytes(content, encoding="utf-8"))
        file_storage_service.save_plan_template_file(result_file, schedule_task_id)
