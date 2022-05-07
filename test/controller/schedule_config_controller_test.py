from src.service import schedule_task_service
from test import log_default_user


def test_update_only_schedule_config_frequency_success(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config()

    new_frequency = 200
    update_data = {
        "frequency": new_frequency,
        "schedule_config_enabled": original_schedule_task.enabled,
    }
    response = a_client.post(
        f"/view/schedule_config/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Configuraci\xc3\xb3n actualizada con \xc3\xa9xito." in response.data
    schedule_task = schedule_task_service.get_schedule_task_config()
    assert schedule_task is not None
    assert schedule_task.frequency == new_frequency
    assert schedule_task.enabled == original_schedule_task.enabled


def test_update_only_schedule_config_enabled_success(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config()

    new_enabled = "false"
    update_data = {
        "frequency": original_schedule_task.frequency,
        "schedule_config_enabled": new_enabled,
    }
    response = a_client.post(
        f"/view/schedule_config/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Configuraci\xc3\xb3n actualizada con \xc3\xa9xito." in response.data
    schedule_task = schedule_task_service.get_schedule_task_config()
    assert schedule_task is not None
    assert schedule_task.frequency == original_schedule_task.frequency
    assert not schedule_task.enabled


def test_update_both_schedule_config_enabled_and_frequencysuccess(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config()

    new_frequency = 200
    new_enabled = "false"
    update_data = {"frequency": new_frequency, "schedule_config_enabled": new_enabled}
    response = a_client.post(
        f"/view/schedule_config/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Configuraci\xc3\xb3n actualizada con \xc3\xa9xito." in response.data
    schedule_task = schedule_task_service.get_schedule_task_config()
    assert schedule_task is not None
    assert not schedule_task.frequency == original_schedule_task.frequency
    assert schedule_task.frequency == new_frequency
    assert not schedule_task.enabled == original_schedule_task.enabled
    assert not schedule_task.enabled


def test_update_fails_on_empty_schedule_frequency(a_client):
    log_default_user(a_client)
    original_schedule_task = schedule_task_service.get_schedule_task_config()

    update_data = {"frequency": None}
    response = a_client.post(
        f"/view/schedule_config/{original_schedule_task.id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b"Error: La frecuencia no puede estar vac\xc3\xada" in response.data
    schedule_task = schedule_task_service.get_schedule_task_config()
    assert schedule_task.frequency == original_schedule_task.frequency
    assert schedule_task.enabled == original_schedule_task.enabled


def test_update_fails_on_invalid_id(a_client):
    log_default_user(a_client)
    invalid_id = -1

    update_data = {"frequency": 200, "schedule_config_enabled": True}
    response = a_client.post(
        f"/view/schedule_config/{invalid_id}",
        data=update_data,
        content_type="multipart/form-data",
    )

    assert b" Error actualizando la configuraci\xc3\xb3n." in response.data


def test_get_schedule_config(a_client):
    log_default_user(a_client)
    schedule_task_config = schedule_task_service.get_schedule_task_config()

    response = a_client.get(f"/view/schedule_config")

    assert b"Configuraci\xc3\xb3n de simulaciones recurrentes<" in response.data
    frequency_info = (
        f'id="frequency" name="frequency" value="{schedule_task_config.frequency}"'
    )
    assert str.encode(frequency_info) in response.data
