import io
import json
from datetime import datetime
from unittest import mock

from src.service import geometry_service
from src.service.exception.file_exception import FileUploadError
from test import log_default_user


def test_add_new_geometry_fails_on_empty_description(a_client, a_geometry_file):
    log_default_user(a_client)
    data = {
        "description": "",
        "file": (io.BytesIO(a_geometry_file), "name.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "name.g01")},
    }

    response = a_client.post(
        "/view/geometry", data=data, content_type="multipart/form-data"
    )

    assert b"Error: Ingrese una descripc" in response.data
    assert geometry_service.get_geometry(3) is None


def test_add_new_geometry_fails_on_too_long_description(a_client, a_geometry_file):
    log_default_user(a_client)
    too_long_description = "a"
    for _ in range(257):
        too_long_description += "a"
    data = {
        "description": too_long_description,
        "file": (io.BytesIO(a_geometry_file), "name.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "name.g01")},
    }

    response = a_client.post(
        "/view/geometry", data=data, content_type="multipart/form-data"
    )

    assert b"entre 1 y 256 caracteres" in response.data
    assert geometry_service.get_geometry(3) is None


def test_add_new_geometry_fails_on_empty_file(a_client, a_geometry_file):
    log_default_user(a_client)
    data = {
        "description": "some_description",
        "files": {"file": (io.BytesIO(a_geometry_file), "test_geometry.g01")},
    }

    response = a_client.post(
        "/view/geometry", data=data, content_type="multipart/form-data"
    )
    assert b"Error: Seleccione un archivo" in response.data
    assert geometry_service.get_geometry(3) is None


@mock.patch("src.service.file_storage_service.save_file")
def test_add_new_geometry_fails_on_upload_file_error(
    save_file, a_client, a_geometry_file
):
    log_default_user(a_client)
    save_file.side_effect = FileUploadError("cualki")

    filename = "test_geometry.g01"
    description = "some_description"
    data = {
        "description": description,
        "file": (io.BytesIO(a_geometry_file), filename),
        "files": {"file": (io.BytesIO(a_geometry_file), filename)},
    }

    response = a_client.post(
        "/view/geometry", data=data, content_type="multipart/form-data"
    )

    assert b"Error cargando archivo" in response.data
    assert geometry_service.get_geometry(3) is None


def test_add_new_geometry_success(a_client, a_geometry_file):
    log_default_user(a_client)
    filename = "test_geometry.g01"
    description = "some_description"
    data = {
        "description": description,
        "file": (io.BytesIO(a_geometry_file), filename),
        "files": {"file": (io.BytesIO(a_geometry_file), filename)},
    }

    response = a_client.post(
        "/view/geometry", data=data, content_type="multipart/form-data"
    )

    assert b"creada con \xc3\xa9xito." in response.data
    geometry = geometry_service.get_geometry(3)
    assert geometry.name == filename
    assert geometry.description == description
    assert geometry.user_id == 1


def test_file_name_secure_on_geometry_creation(a_client, a_geometry_file):
    log_default_user(a_client)
    data = {
        "description": "some_description",
        "file": (io.BytesIO(a_geometry_file), "test geometry.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "test geometry.g01")},
    }

    a_client.post("/view/geometry", data=data, content_type="multipart/form-data")

    geometry = geometry_service.get_geometry(3)
    assert geometry.name == "test_geometry.g01"


@mock.patch("src.service.geometry_service.get_geometries")
def test_list_geometries_when_there_are_none(get_geometries, a_client):
    get_geometries.return_value = []
    log_default_user(a_client)

    response = a_client.get("/geometry")

    expected_response = {
        "rows": [],
        "total": 0,
    }

    assert json.loads(response.data) == expected_response


def test_list_geometries_when_there_only_two(a_client):
    log_default_user(a_client)
    response = a_client.get("/geometry")
    expected_response = {
        "rows": [
            {
                "created_at": datetime.now().strftime("%d/%m/%Y"),
                "description": "Geometría Paraná",
                "id": 2,
                "name": "DeltaParana_2017.g23",
                "user": "Admin Ina",
            },
            {
                "created_at": "21/12/2021",
                "description": "Ejemplo dado por el INA",
                "id": 1,
                "name": "Modelo1-Atucha.g01",
                "user": "Admin Ina",
            },
        ],
        "total": 2,
    }

    response_json = json.loads(response.data)
    rows = response_json["rows"]
    assert response_json["total"] == expected_response["total"]
    assert rows[0]["id"] == expected_response["rows"][0]["id"]
    assert rows[0]["description"] == expected_response["rows"][0]["description"]
    assert rows[0]["user"] == expected_response["rows"][0]["user"]
    assert rows[1]["id"] == expected_response["rows"][1]["id"]
    assert rows[1]["description"] == expected_response["rows"][1]["description"]
    assert rows[1]["user"] == expected_response["rows"][1]["user"]


def test_list_geometries_when_there_two(a_client, a_geometry_file):
    log_default_user(a_client)
    test_add_new_geometry_success(a_client, a_geometry_file)

    response = a_client.get("/geometry")
    expected_response = {
        "rows": [
            {
                "created_at": datetime.now().strftime("%d/%m/%Y"),
                "description": "some_description",
                "id": 3,
                "name": "test_geometry.g01",
                "user": "Admin Ina",
            },
            {
                "created_at": datetime.now().strftime("%d/%m/%Y"),
                "description": "Geometría Paraná",
                "id": 2,
                "name": "DeltaParana_2017.g23",
                "user": "Admin Ina",
            },
            {
                "created_at": "21/12/2021",
                "description": "Ejemplo dado por el INA",
                "id": 1,
                "name": "Modelo1-Atucha.g01",
                "user": "Admin Ina",
            },
        ],
        "total": 3,
    }

    response_json = json.loads(response.data)
    rows = response_json["rows"]
    assert response_json["total"] == expected_response["total"]
    assert rows[0]["description"] == expected_response["rows"][0]["description"]
    assert rows[0]["id"] == expected_response["rows"][0]["id"]
    assert rows[0]["user"] == expected_response["rows"][0]["user"]
    assert rows[1]["description"] == expected_response["rows"][1]["description"]
    assert rows[1]["id"] == expected_response["rows"][1]["id"]
    assert rows[1]["user"] == expected_response["rows"][1]["user"]
    assert rows[2]["description"] == expected_response["rows"][2]["description"]
    assert rows[2]["id"] == expected_response["rows"][2]["id"]
    assert rows[2]["user"] == expected_response["rows"][2]["user"]
