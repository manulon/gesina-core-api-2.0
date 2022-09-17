from src.scheduler import ScheduledTaskJob
from src.service import execution_plan_service
import io


def test_scheduler_execute():
    job = ScheduledTaskJob(1)

    job.simulate(flow_file=io.BytesIO())

    assert execution_plan_service.get_execution_plan(2) is not None
