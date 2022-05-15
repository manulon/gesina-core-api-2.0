from unittest.mock import MagicMock

import pytest

from src.persistance import User
from src.persistance.scheduled_task import ScheduledTask
from datetime import datetime


def test_scheduler_execute():
    mocker = MagicMock()
    user = User()
    user.id = 1
    user.first_name = "test_user"
    user.last_name = "test_user"

    scheduled_task = ScheduledTask()
    scheduled_task.geometry_id = 1
    scheduled_task.name = "scheduled_test"
    scheduled_task.frequency = 60
    scheduled_task.user = user
    scheduled_task.start_datetime = datetime.now()

    mocker.patch("src.persistance.session.get_session", return_value=MagicMock())
    from src.scheduler import ScheduledTaskJob

    mock_copy_geometry = mocker.patch(
        "src.service.file_storage_service.copy_geometry_to", return_value=None
    )

    mock_save_file = mocker.patch(
        "src.persistance.session.get_session", return_value=None
    )

    mock_update_execution = mocker.patch(
        "src.service.execution_plan_service.update_execution_plan_status",
        return_value=None,
    )

    mock_fake_execution = mocker.patch("src.tasks.fake_simulate", return_value=None)

    job = ScheduledTaskJob(scheduled_task)

    job.simulate()

    assert mock_copy_geometry.call_count == 1
    assert mock_save_file.call_count == 3
    assert mock_update_execution.call_count == 1
    assert mock_fake_execution.call_count == 1
