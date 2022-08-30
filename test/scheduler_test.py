from src.scheduler import ScheduledTaskJob
from src.service import execution_plan_service


def test_scheduler_execute():
    job = ScheduledTaskJob(1)

    job.simulate()

    assert execution_plan_service.get_execution_plan(2) is not None
