import pytest

from src.persistance import User
from src.persistance.scheduled_task import ScheduledTask
from datetime import datetime

from src.service import execution_plan_service


def test_scheduler_execute():
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

    from src.scheduler import ScheduledTaskJob

    job = ScheduledTaskJob(scheduled_task)

    job.simulate()

    assert execution_plan_service.get_execution_plan(2) is not None
