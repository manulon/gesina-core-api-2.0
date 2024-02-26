import io

from src.service import file_storage_service

LINES_TO_PROCESS = [
    "Proj Title",
    "DSS Start Date",
    "DSS Start Time",
    "DSS End Date",
    "DSS End Time",
    "Unsteady File",
    "Plan File",
    "Current Plan",
]

LINES_CHANGES = {
    "Proj Title": "Proj Title=$PROJECT_TITLE",
    "DSS Start Date": "DSS Start Date=$START_DATE",
    "DSS Start Time": "DSS Start Time=$START_TIME",
    "DSS End Date": "DSS End Date=$END_DATE",
    "DSS End Time": "DSS End Time=$END_TIME",
    "Unsteady File": "Unsteady File=u01",
    "Plan File": "Plan File=p01",
    "Current Plan": "Current Plan=p01",
}


def process_project_template(project_file, schedule_task_id):
    if project_file:
        content = ""
        decoded_file = project_file.read().decode("utf-8")

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
        return file_storage_service.save_project_template_file(result_file, schedule_task_id)
