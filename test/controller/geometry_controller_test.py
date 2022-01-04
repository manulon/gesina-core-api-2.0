def test_add_new_geometry(a_client, a_geometry_file):
    data = {"form": {"description": "Una descrip"}, "files": {"file": a_geometry_file}}

    response = a_client.post("/geometry", data=data, content_type="multipart/form-data")

    assert b"creada con &eacute;xito." in response.data
