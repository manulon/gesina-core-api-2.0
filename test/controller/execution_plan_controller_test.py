import io
from datetime import datetime, timedelta

from src.persistance.execution_plan import ExecutionPlanStatus
from src.service import execution_plan_service
from test import log_default_user


def test_add_new_execution_plan_fails_on_empty_plan_name(a_client):
    log_default_user(a_client)
    data = {
        "plan_name": "",
    }

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese un nombre de plan" in response.data
    assert execution_plan_service.get_execution_plan(2) is None


def test_add_new_execution_plan_fails_on_empty_geometry_option(a_client):
    log_default_user(a_client)
    data = {"plan_name": "some_plan", "geometry_option": None}

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese un nombre de plan" not in response.data
    assert b"Error: Seleccione una geometr" in response.data
    assert execution_plan_service.get_execution_plan(2) is None


def test_add_new_execution_plan_fails_on_empty_flow_file(a_client):
    log_default_user(a_client)
    data = {"plan_name": "some_plan", "geometry_option": 1}

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese un nombre de plan" not in response.data
    assert b"Error: Seleccione una geometr" not in response.data
    assert b"Error: Seleccione un archivo" in response.data
    assert execution_plan_service.get_execution_plan(2) is None


def test_add_new_execution_plan_fails_on_empty_start_dates(a_client, a_flow_file):
    log_default_user(a_client)
    file = (io.BytesIO(a_flow_file), "flow.b01")
    data = {
        "plan_name": "some_plan",
        "geometry_option": 1,
        "flow_file": file,
        "files": {"file": file},
    }

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese un nombre de plan" not in response.data
    assert b"Error: Seleccione una geometr" not in response.data
    assert b"Error: Seleccione un archivo" not in response.data
    assert b"Error: Seleccione una fecha desde" in response.data
    assert execution_plan_service.get_execution_plan(2) is None


def test_add_new_execution_plan_fails_on_invalid_dates(a_client, a_flow_file):
    log_default_user(a_client)
    file = (io.BytesIO(a_flow_file), "flow.b01")
    data = {
        "plan_name": "some_plan",
        "geometry_option": 1,
        "flow_file": file,
        "files": {"file": file},
        "start_date": datetime.now().strftime("%d/%m/%Y"),
        "end_date": (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y"),
    }

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese un nombre de plan" not in response.data
    assert b"Error: Seleccione una geometr" not in response.data
    assert b"Error: Seleccione un archivo" not in response.data
    assert (
        b"Error: &#34;Fecha desde&#34; debe ser menor a la &#34;fecha hasta&#34;"
        in response.data
    )
    assert execution_plan_service.get_execution_plan(2) is None


def test_add_new_execution_plan_fails_on_invalid_geometry_option(a_client, a_flow_file):
    log_default_user(a_client)
    file = (io.BytesIO(a_flow_file), "flow.b01")
    data = {
        "plan_name": "some_plan",
        "geometry_option": 5,
        "flow_file": file,
        "files": {"file": file},
        "start_date": datetime.now().strftime("%d/%m/%Y"),
        "end_date": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"),
    }

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese un nombre de plan" not in response.data
    assert b"Error: Seleccione una geometr" not in response.data
    assert b"Error: Seleccione un archivo" not in response.data
    assert (
        b"Error: &#34;Fecha desde&#34; debe ser menor a la &#34;fecha hasta&#34;"
        not in response.data
    )
    assert b"Error guardando informaci\xc3\xb3n en la base de datos." in response.data
    assert execution_plan_service.get_execution_plan(2) is None


def test_add_new_execution_plan_success(a_client, a_flow_file):
    log_default_user(a_client)
    file = (io.BytesIO(a_flow_file), "flow.b01")
    start_datetime = datetime.now()
    end_datetime = start_datetime + timedelta(days=1)
    data = {
        "plan_name": "some_plan",
        "geometry_option": 1,
        "flow_file": file,
        "files": {"file": file},
        "start_date": start_datetime.strftime("%d/%m/%Y"),
        "end_date": end_datetime.strftime("%d/%m/%Y"),
    }

    response = a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )

    assert b"creada con \xc3\xa9xito." in response.data
    execution_plan = execution_plan_service.get_execution_plan(2)
    assert execution_plan is not None
    assert execution_plan.plan_name == "some_plan"
    assert execution_plan.geometry_id == 1
    assert execution_plan.user_id == 1
    assert execution_plan.start_datetime.day == start_datetime.day
    assert execution_plan.end_datetime.day == end_datetime.day
    assert execution_plan.status == ExecutionPlanStatus.PENDING
