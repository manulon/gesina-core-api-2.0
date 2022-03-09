from pytz import utc

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from src import config

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
    def __init__(self, name):
        self.name = name

    def simulate(self):
        print(f"Simulando {self.name}")


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
            scheduler.add_job(Job(st.name).simulate, "interval", seconds=10, id=str(st.id))
        else:
            print(f"Already in scheduler {st.name}")


scheduler.add_job(check_for_scheduled_tasks, "interval", seconds=10)

scheduler.start()
