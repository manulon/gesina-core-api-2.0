import logging

from pytz import utc, timezone
from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from src.service import execution_plan_service
from src import config
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service.execution_plan_service import update_execution_plan_status
from src.service.schedule_task_service import get_schedule_task_config
from src.tasks import queue_or_fake_simulate

from src.util.file_builder import build_project, build_plan, new_build_flow

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
FORECAST_LAG_HOURS = 12

logger = logging.getLogger("apscheduler")


class ScheduledTaskJob:
    def __init__(self, task_id: int):
        self.scheduled_task = task_id

    def simulate(self, flow_file=None):
        scheduled_task = get_schedule_task_config(self.scheduled_task)
        logger.error("Starting simulation")
        locale = timezone("America/Argentina/Buenos_Aires")
        today = datetime.now(tz=locale).replace(minute=0,second=0,microsecond=0) - timedelta(hours=FORECAST_LAG_HOURS) # .replace(minute=0)
        start_date = today - timedelta(scheduled_task.observation_days)
        end_date = today + timedelta(scheduled_task.forecast_days)
        logger.error(f"Start Date: {start_date} and End Date: {end_date}")

        simulation_name = f'{scheduled_task.name.replace(" ", "_")}-{start_date.strftime("%Y%m%d_%Hhs")}'

        project_file = build_project(
            scheduled_task.id, simulation_name, start_date, end_date
        )
        project_name = "scheduled-task.prj"

        plan_file = build_plan(scheduled_task.id, simulation_name, start_date, end_date)
        plan_name = "scheduled-task.p01"

        use_restart = scheduled_task.start_condition_type == "restart_file"

        # flow_file = flow_file or build_flow(
        #     use_restart=use_restart, initial_flows=scheduled_task.initial_flows
        # )

        flow_file = flow_file or new_build_flow(
            scheduled_task.border_conditions,
            use_restart,
            "restart_file.rst",
            scheduled_task.initial_flows,
            scheduled_task.calibration_id,
            start_date,
            end_date,
        )
        flow_name = "scheduled_task.u01"

        execution_plan = execution_plan_service.create_from_scheduler(
            simulation_name,
            scheduled_task.geometry_id,
            scheduled_task.user,
            project_name,
            project_file,
            plan_name,
            plan_file,
            flow_name,
            flow_file,
            use_restart,
            scheduled_task.id,
            scheduled_task.plan_series_list,
        )
        update_execution_plan_status(execution_plan.id, ExecutionPlanStatus.RUNNING)
        try:
            queue_or_fake_simulate(
                execution_plan.id, scheduled_task.calibration_id_for_simulations
            )
        except Exception as e:
            logger.error(f"Error: {e}")


def check_for_scheduled_tasks():
    from src.persistance.session import get_session
    from src.persistance.scheduled_task import ScheduledTask

    with get_session() as session:
        scheduled_tasks = session.query(ScheduledTask).all()

    for st in scheduled_tasks:
        all_jobs_ids = [j.id for j in scheduler.get_jobs()]
        job_id = str(st.id)

        if (
            job_id not in all_jobs_ids
            and st.start_datetime < datetime.now()
            and st.enabled
        ):
            logger.info(f"Adding {st.name}")
            scheduler.add_job(
                ScheduledTaskJob(st.id).simulate,
                "interval",
                minutes=st.frequency,
                id=job_id,
            )
        elif job_id in all_jobs_ids:

            job = scheduler.get_job(job_id)
            interval = timedelta(minutes=st.frequency)
            changed_interval = job.trigger.interval != interval

            if changed_interval:
                logging.info(f"Updating interval for {st.name} with {interval}")
                scheduler.reschedule_job(
                    job_id, trigger="interval", minutes=st.frequency
                )

            if not st.enabled:
                logger.info(f"Removing {st.name}")
                scheduler.remove_job(job_id)


if __name__ == "__main__":
    scheduler.add_job(check_for_scheduled_tasks, "interval", seconds=10)
    scheduler.start()
