import pytest

from src.app import app


@pytest.fixture(scope="session")
def a_client():
    app.config["TESTING"] = True
    yield app.test_client()
