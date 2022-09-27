import pytest

from src.service import user_service
from test import log_default_user


def test_do_create_user_without_email_fails(a_client):
    log_default_user(a_client)

    users_size_before = len(user_service.get_users(limit=5))
    data = {
        "first_name": "John",
        "last_name": "Salshi",
        "password": "123456",
        "repeat_password": "123456",
        "admin_role": False,
    }
    response = a_client.post(
        "/user/register", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese un email" in response.data
    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before


def test_do_sign_up_without_names_fails(a_client):
    log_default_user(a_client)

    users_size_before = len(user_service.get_users(limit=5))
    data = {
        "email": "hola@mundo.com",
        "password": "123456",
        "repeat_password": "123456",
        "admin_role": False,
    }
    response = a_client.post(
        "/user/register", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese un nombre" in response.data
    assert b"Ingrese un apellido" in response.data
    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before


def test_do_sign_up_without_passwords_fails(a_client):
    log_default_user(a_client)

    users_size_before = len(user_service.get_users(limit=5))
    data = {"email": "hola@mundo.com", "first_name": "John", "last_name": "Salshi", "admin_role": False,}
    response = a_client.post(
        "/user/register", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese una contrase\xc3\xb1a" in response.data
    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before


def test_do_sign_up_success(a_client):
    log_default_user(a_client)

    users_size_before = len(user_service.get_users(limit=5))
    data = {
        "email": "hola@mundo.com",
        "first_name": "John",
        "last_name": "Salshi",
        "password": "123456",
        "repeat_password": "123456",
        "admin_role": False,
    }
    response = a_client.post(
        "/user/register", data=data, content_type="multipart/form-data"
    )

    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before + 1
