import pytest

from src.app import app


@pytest.fixture(scope="session")
def a_client():
    app.config["TESTING"] = True
    yield app.test_client()


@pytest.fixture()
def a_geometry_file():
    with open("test/resources/dummy_geometry.g01", "rb") as f:
        return f.read()
