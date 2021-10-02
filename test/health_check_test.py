from http import HTTPStatus


def test_test(a_client):
    response = a_client.get("health-check")
    assert response.status_code == HTTPStatus.OK
