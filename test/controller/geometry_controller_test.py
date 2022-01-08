import io


def test_add_new_geometry_fails_on_empty_description(a_client, a_geometry_file):
    data = {
        "form": {"description": None},
        "file": (io.BytesIO(a_geometry_file), "name.g01"),
        "files": {"file": (io.BytesIO(a_geometry_file), "name.g01")},
    }

    response = a_client.post("/geometry", data=data, content_type="multipart/form-data")
    assert b"Error: Ingrese una descripc" in response.data


# def test_add_new_geometry_fails_on_empty_file(a_client, a_geometry_file):
#     data = {"form": {"description": "Una descrip"}, "files": {"file": a_geometry_file}}
#
#     response = a_client.post("/geometry", data=data, content_type="multipart/form-data")
#
#     assert b'Error: Seleccione un archivo' in response.data
#
#
# def test_add_new_geometry(a_client, a_geometry_file):
#     data = {"form": {"description": "Una descrip"}, "files": {"file": a_geometry_file}}
#
#     response = a_client.post("/geometry", data=data, content_type="multipart/form-data")
#
#     assert '201' in response.status
