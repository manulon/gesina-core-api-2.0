import csv
import io
from src.persistance.scheduled_task import (
    InitialFlow,
)
from src.persistance.session import get_session
from src.service import file_storage_service
from src.service.exception.file_exception import FileUploadError

INITIAL_FLOW_CSV_HEADER = ["river", "reach", "river_stat", "flow"]


def retrieve_initial_flows_from_form(form, scheduled_config_id=None):
    from_csv = process_initial_flows_csv_file(
        form.initial_flow_file.data, scheduled_config_id
    )
    from_form = process_initial_flows_form(form.initial_flow_list, scheduled_config_id)
    return from_csv + from_form


def retrieve_initial_flows_json(initial_flow_file, initial_flow_list, scheduled_config_id=None):
    from_csv = process_initial_flows_csv_file(file_storage_service.get_file(initial_flow_file), scheduled_config_id)
    from_json = process_initial_flows_json(initial_flow_list, scheduled_config_id)
    return from_csv + from_json


def create_initial_flows_from_form(form):
    if form.start_condition_type.data == "restart_file":
        # TODO manejar logica para el restart file
        do = "something"

    return retrieve_initial_flows_from_form(form)


def create_initial_flows_from_json(start_condition_type, initial_flow_file, initial_flow_list):
    if start_condition_type == "restart_file":
        do = "nothing"
    return retrieve_initial_flows_json(initial_flow_file, initial_flow_list)


def update_initial_flows(session, scheduled_config_id, initial_flows):
    session.query(InitialFlow).filter_by(scheduled_task_id=scheduled_config_id).delete()
    for each_initial_flow in initial_flows:
        session.add(each_initial_flow)


def update_initial_flow(initial_flow, new_initial_flow):
    # TODO validate values
    for key, value in new_initial_flow.items():
        if key in INITIAL_FLOW_CSV_HEADER:
            setattr(initial_flow, key, value)


def process_initial_flows_form(initial_flow_list, scheduled_config_id=None):
    result = []
    for each_initial_flow in initial_flow_list:
        if scheduled_config_id:
            initial_flow = InitialFlow(
                scheduled_task_id=scheduled_config_id,
                river=each_initial_flow.river.data,
                reach=each_initial_flow.reach.data,
                river_stat=each_initial_flow.river_stat.data,
                flow=each_initial_flow.flow.data,
            )
        else:
            initial_flow = InitialFlow(
                river=each_initial_flow.river.data,
                reach=each_initial_flow.reach.data,
                river_stat=each_initial_flow.river_stat.data,
                flow=each_initial_flow.flow.data,
            )
        result.append(initial_flow)
    return result


def process_initial_flows_json(initial_flow_list, scheduled_config_id=None):
    result = []
    if initial_flow_list is None:
        return result
    for each_initial_flow in initial_flow_list:
        if scheduled_config_id:
            initial_flow = InitialFlow(
                scheduled_task_id=scheduled_config_id,
                river=each_initial_flow.get("river"),
                reach=each_initial_flow.get("reach"),
                river_stat=each_initial_flow.get("river_stat"),
                flow=each_initial_flow.get("flow"),
            )
        else:
            initial_flow = InitialFlow(
                river=each_initial_flow.get("river"),
                reach=each_initial_flow.get("reach"),
                river_stat=each_initial_flow.get("river_stat"),
                flow=each_initial_flow.get("flow"),
            )
        result.append(initial_flow)
    return result


def add_initial_flow_to_scheduled_task(oneSeries, scheduled_config_id):
    if not scheduled_config_id:
        raise Exception("Scheduled config id not present while adding new border series")
    initial_flow_list = process_initial_flows_json([oneSeries],scheduled_config_id)
    with get_session() as session:
        session.add(initial_flow_list[0])



def process_initial_flows_csv_file(initial_flow_file, scheduled_config_id=None):
    result = []
    if initial_flow_file:
        buffer = initial_flow_file.read()
        content = buffer.decode()
        file = io.StringIO(content)
        csv_data = csv.reader(file, delimiter=",")
        header = next(csv_data)
        if len(header) >= 4 and header[:4] == INITIAL_FLOW_CSV_HEADER:
            for row in csv_data:
                if scheduled_config_id:
                    initial_flow = InitialFlow(
                        scheduled_task_id=scheduled_config_id,
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        flow=row[3],
                    )
                else:
                    initial_flow = InitialFlow(
                        river=row[0],
                        reach=row[1],
                        river_stat=row[2],
                        flow=row[3],
                    )
                result.append(initial_flow)
        else:
            raise FileUploadError("Error: Archivo .csv inválido - Initial flow service")
    if initial_flow_file is not None:
        initial_flow_file.seek(0)
    return result
