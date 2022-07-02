from datetime import datetime

from src.service import schedule_task_service
from test import log_default_user

DEFAULT_SCHEDULE_TASK_ID = 1


def test_update_only_schedule_config_frequency_success(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )

    new_frequency = 200
    update_data = {
        "frequency": new_frequency,
        "enabled": original_schedule_task.enabled,
        "name": original_schedule_task.name,
        "description": original_schedule_task.description,
        "start_datetime": original_schedule_task.start_datetime.strftime(
            "%Y-%m-%dT%H:%M"
        ),
        "geometry_id": original_schedule_task.geometry_id,
    }
    response = a_client.post(
        f"/view/schedule_tasks/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )

    assert b"Configuraci%C3%B3n+actualizada+con+%C3%A9xito." in response.data
    assert schedule_task is not None
    assert schedule_task.frequency == new_frequency
    assert schedule_task.enabled == original_schedule_task.enabled


def test_update_only_enabled_success(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )

    new_enabled = "false"
    update_data = {
        "frequency": original_schedule_task.frequency,
        "enabled": new_enabled,
        "name": original_schedule_task.name,
        "description": original_schedule_task.description,
        "start_datetime": original_schedule_task.start_datetime.strftime(
            "%Y-%m-%dT%H:%M"
        ),
        "geometry_id": original_schedule_task.geometry_id,
    }
    response = a_client.post(
        f"/view/schedule_tasks/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Configuraci%C3%B3n+actualizada+con+%C3%A9xito." in response.data
    schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )
    assert schedule_task is not None
    assert schedule_task.frequency == original_schedule_task.frequency
    assert not schedule_task.enabled


def test_update_both_enabled_and_frequency_success(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )

    new_frequency = 200
    new_enabled = "false"
    update_data = {
        "frequency": new_frequency,
        "enabled": new_enabled,
        "name": original_schedule_task.name,
        "description": original_schedule_task.description,
        "start_datetime": original_schedule_task.start_datetime.strftime(
            "%Y-%m-%dT%H:%M"
        ),
        "geometry_id": original_schedule_task.geometry_id,
    }

    response = a_client.post(
        f"/view/schedule_tasks/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Configuraci%C3%B3n+actualizada+con+%C3%A9xito." in response.data
    schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )
    assert schedule_task is not None
    assert not schedule_task.frequency == original_schedule_task.frequency
    assert schedule_task.frequency == new_frequency
    assert not schedule_task.enabled == original_schedule_task.enabled
    assert not schedule_task.enabled


def test_update_fails_on_empty_schedule_frequency(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )

    update_data = {"frequency": None}
    response = a_client.post(
        f"/view/schedule_tasks/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Error: La frecuencia no puede estar vac\xc3\xada" in response.data
    schedule_task = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )
    assert schedule_task.frequency == original_schedule_task.frequency
    assert schedule_task.enabled == original_schedule_task.enabled


def test_update_fails_on_invalid_id(a_client):
    log_default_user(a_client)
    invalid_id = -1

    update_data = {
        "frequency": 200,
        "enabled": True,
        "name": "foo",
        "description": "bar",
        "start_datetime": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "geometry_id": "1",
    }
    response = a_client.post(
        f"/view/schedule_tasks/{invalid_id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b" Error actualizando la configuraci\xc3\xb3n." in response.data


def test_get_schedule_config(a_client):
    log_default_user(a_client)
    schedule_task_config = schedule_task_service.get_schedule_task_config(
        DEFAULT_SCHEDULE_TASK_ID
    )

    response = a_client.get(f"/view/schedule_tasks/{DEFAULT_SCHEDULE_TASK_ID}")

    assert b"Configuraci\xc3\xb3n de simulaciones recurrentes<" in response.data

    frequency_info = f'<input class="form-control" id="frequency" min="5" name="frequency" required type="number" value="{schedule_task_config.frequency}">'
    assert str.encode(frequency_info) in response.data
