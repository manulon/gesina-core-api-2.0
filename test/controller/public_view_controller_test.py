from src.service import user_service


def test_do_sign_in_with_valid_credentials(a_client):
    user_to_login = user_service.get_user(1)
    data = {"email": user_to_login.email, "password": "123456"}
    response = a_client.post(
        "/view/login", data=data, content_type="multipart/form-data"
    )

    assert b"/view/" in response.data
    assert user_to_login.is_authenticated


def test_do_sign_in_with_invalid_credentials(a_client):
    user_to_login = user_service.get_user(1)
    data = {"email": user_to_login.email, "password": "some_wrong_password"}

    response = a_client.post(
        "/view/login", data=data, content_type="multipart/form-data"
    )

    assert b"Usuario/contrase\xc3\xb1a inv\xc3\xa1lido" in response.data
    # assert not user_to_login.is_authenticated


def test_do_sign_in_with_no_password(a_client):
    user_to_login = user_service.get_user(1)
    data = {"email": user_to_login.email}
    response = a_client.post(
        "/view/login", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese una contrase\xc3\xb1a" in response.data
    # assert not user_to_login.is_authenticated


def test_do_sign_up_without_email_fails(a_client):
    users_size_before = len(user_service.get_users(limit=5))
    data = {
        "first_name": "John",
        "last_name": "Salshi",
        "password": "123456",
        "repeat_password": "123456",
    }
    response = a_client.post(
        "/view/sign-up", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese un email" in response.data
    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before


def test_do_sign_up_without_names_fails(a_client):
    users_size_before = len(user_service.get_users(limit=5))
    data = {
        "email": "hola@mundo.com",
        "password": "123456",
        "repeat_password": "123456",
    }
    response = a_client.post(
        "/view/sign-up", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese un nombre" in response.data
    assert b"Ingrese un apellido" in response.data
    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before


def test_do_sign_up_without_passwords_fails(a_client):
    users_size_before = len(user_service.get_users(limit=5))
    data = {"email": "hola@mundo.com", "first_name": "John", "last_name": "Salshi"}
    response = a_client.post(
        "/view/sign-up", data=data, content_type="multipart/form-data"
    )

    assert b"Ingrese una contrase\xc3\xb1a" in response.data
    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before


def test_do_sign_up_success(a_client):
    users_size_before = len(user_service.get_users(limit=5))
    data = {
        "email": "hola@mundo.com",
        "first_name": "John",
        "last_name": "Salshi",
        "password": "123456",
        "repeat_password": "123456",
    }
    response = a_client.post(
        "/view/sign-up", data=data, content_type="multipart/form-data"
    )

    users_size_after = len(user_service.get_users(limit=5))
    assert users_size_after == users_size_before + 1
