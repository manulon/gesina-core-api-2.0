import io

import pytest

from src.app import app
from test import log_default_user


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


@pytest.fixture()
def a_flow_file():
    with open("test/resources/dummy_flow.u01", "rb") as f:
        return f.read()


@pytest.fixture()
def a_project_file():
    with open("test/resources/dummy_project.prj", "rb") as f:
        return f.read()


@pytest.fixture()
def a_plan_file():
    with open("test/resources/dummy_plan.p01", "rb") as f:
        return f.read()


@pytest.fixture()
def a_execution_plan(a_client, a_project_file, a_plan_file, a_flow_file):
    log_default_user(a_client)
    project_file = (io.BytesIO(a_project_file), "project.prj")
    plan_file = (io.BytesIO(a_plan_file), "plan.p01")
    flow_file = (io.BytesIO(a_flow_file), "flow.u01")

    data = {
        "plan_name": "some_plan",
        "geometry_option": 1,
        "project_file": project_file,
        "plan_file": plan_file,
        "flow_file": flow_file,
    }

    return a_client.post(
        "/view/execution_plan", data=data, content_type="multipart/form-data"
    )
