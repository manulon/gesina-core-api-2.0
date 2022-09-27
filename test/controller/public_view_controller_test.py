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
