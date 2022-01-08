import pytest

from src.app import app


@pytest.fixture(autouse=True)
def run_around_test():
    from src import migrate, rollback

    migrate()
    yield
    rollback()


@pytest.fixture(scope="session")
def a_client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    yield app.test_client()


@pytest.fixture()
def a_geometry_file():
    with open("test/resources/dummy_geometry.g01", "rb") as f:
        return f.read()
