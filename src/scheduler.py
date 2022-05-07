from pytz import utc
from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from src.service import execution_plan_service, user_service
from src import config
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service.execution_plan_service import update_execution_plan_status
from src.tasks import queue_or_fake_simulate
from io import StringIO

from src.util.file_builder import build_project, build_plan

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

SIMULATION_DURATION = 60


class ScheduledTaskJob:
    def __init__(self, task):
        self.scheduled_task = task

    def simulate(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=SIMULATION_DURATION)

        simulation_name = f'{self.scheduled_task.name.replace(" ", "_")}-{start_date.strftime("%Y%m%d_%Hhs")}'

        user = user_service.get_admin_user()
        geometry_id = 1
        project_file = build_project(simulation_name, start_date, end_date)
        project_name = "scheduled_task.prj"
        plan_file = build_plan(simulation_name, start_date, end_date)
        plan_name = "scheduled_task.p01"
        flow_file = StringIO(
            "This is the Flow File"
        )  # Armar Flow File desde el módulo de Marian
        flow_name = "scheduled_task.u01"

        execution_plan = execution_plan_service.create_from_scheduler(
            simulation_name,
            geometry_id,
            user,
            project_name,
            project_file,
            plan_name,
            plan_file,
            flow_name,
            flow_file,
        )
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
                lambda: start_scheduled_task(st),
                "date",
                run_date=st.start_datetime,
                id=str(st.id),
            )
        else:
            print(f"Already in scheduler {st.name}")


def start_scheduled_task(st):
    scheduler.add_job(
        ScheduledTaskJob(st).simulate, "interval", seconds=st.frequency, id=str(st.id)
    )


scheduler.add_job(check_for_scheduled_tasks, "interval", seconds=10)

scheduler.start()
