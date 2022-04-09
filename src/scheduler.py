from pytz import utc

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from src.service import execution_plan_service
from src import config
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service.execution_plan_service import update_execution_plan_status
from src.tasks import queue_or_fake_simulate

jobstores = {
    "default": SQLAlchemyJobStore(
        url=f"postgresql://{config.database_user}:{config.database_password}@{config.database_host}/{config.database_name}",
        engine_options={
            "connect_args": {
                "options": f"-csearch_path={config.scheduler_database_schema}"
            }
        },
    )
}

executors = {
    "default": ThreadPoolExecutor(2),
}

job_defaults = {"coalesce": True, "max_instances": 1}

scheduler = BlockingScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
)


class Job:
    def __init__(self, task):
        self.task = task

    def simulate(self):
        print(f"Ajusto los .u de la corrida {self.task.name}")
        form = 'paquita'
        execution_plan = execution_plan_service.create(form)
        update_execution_plan_status(execution_plan.id, ExecutionPlanStatus.RUNNING)
        queue_or_fake_simulate(execution_plan.id)


def check_for_scheduled_tasks():
    from src.persistance.session import get_session
    from src.persistance.scheduled_task import ScheduledTask

    with get_session() as session:
        scheduled_tasks = session.query(ScheduledTask).filter_by(enabled=True).all()

    for st in scheduled_tasks:
        print(f"Found {st.name} for execution")
        all_jobs_ids = [j.id for j in scheduler.get_jobs()]
        if str(st.id) not in all_jobs_ids:
            print(f"Adding {st.name}")
            scheduler.add_job(
                lambda: start_scheduled_task(st), "date", run_date=st.start_datetime, id=str(st.id)
            )
        else:
            print(f"Already in scheduler {st.name}")


def start_scheduled_task(st):
    scheduler.add_job(
        Job(st).simulate, "interval", seconds=st.frequency, id=str(st.id)
    )


scheduler.add_job(check_for_scheduled_tasks, "interval", seconds=10)

scheduler.start()
