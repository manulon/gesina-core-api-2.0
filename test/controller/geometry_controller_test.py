import io


def test_add_new_geometry_fails_on_empty_description(a_client, a_geometry_file):
    data = {
        "description": "",
        "file": (io.BytesIO(a_geometry_file), "name.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "name.g01")},
    }

    response = a_client.post("/geometry", data=data, content_type="multipart/form-data")

    assert b"Error: Ingrese una descripc" in response.data


def test_add_new_geometry_fails_on_too_long_description(a_client, a_geometry_file):
    too_long_description = "a"
    for _ in range(257):
        too_long_description += "a"
    data = {
        "description": too_long_description,
        "file": (io.BytesIO(a_geometry_file), "name.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "name.g01")},
    }

    response = a_client.post("/geometry", data=data, content_type="multipart/form-data")

    assert b"entre 1 y 256 caracteres" in response.data


def test_add_new_geometry_fails_on_empty_file(a_client, a_geometry_file):
    data = {
        "description": "some_description",
        "files": {"file": (io.BytesIO(a_geometry_file), "test_geometry.g01")},
    }

    response = a_client.post("/geometry", data=data, content_type="multipart/form-data")
    assert b"Error: Seleccione un archivo" in response.data


def test_add_new_geometry_success(a_client, a_geometry_file):
    data = {
        "description": "some_description",
        "file": (io.BytesIO(a_geometry_file), "test_geometry.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "test_geometry.g01")},
    }

    response = a_client.post("/geometry", data=data, content_type="multipart/form-data")

    assert b"creada con \xc3\xa9xito." in response.data
