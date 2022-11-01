import io

from celery import Celery
from datetime import datetime, timedelta
import os
from src import logger, config
from src.persistance.execution_plan import ExecutionPlanStatus
from src.service import execution_plan_service, notification_service
from src.service.file_storage_service import FileType

os.environ.setdefault("CELERY_CONFIG_MODULE", "src.celery_config")

celery_app = Celery()
celery_app.config_from_envvar("CELERY_CONFIG_MODULE")


@celery_app.task
def simulate(execution_id, user_id):
    import win32com.client as client
    import pandas as pd
    from src.service import file_storage_service

    begin = datetime.now()

    base_path = f"C:\\gesina\\{execution_id}"

    file_storage_service.download_files_for_execution(base_path, execution_id)

    logger.info("Loading hec ras")
    RC = None
    try:
        RC = client.Dispatch("RAS507.HECRASCONTROLLER")
        hec_prj = f"{base_path}\\{execution_id}.prj"
        logger.info("Opening project")
        RC.Project_Open(hec_prj)
        logger.info("Obtaining projects names")
        blnIncludeBasePlansOnly = True
        plan_names = RC.Plan_Names(None, None, blnIncludeBasePlansOnly)[1]

        for name in plan_names:
            logger.info(f"Running plan {name}")
            RC.Plan_SetCurrent(name)
            RC.Compute_HideComputationWindow()
            RC.Compute_CurrentPlan(None, None, True)

        logger.info(f"End of simulation")
        execution_plan = execution_plan_service.get_execution_plan(execution_id)
        execution_plan_output_list = execution_plan.execution_plan_output_list

        dfs = []

        if execution_plan_output_list:
            for epo in execution_plan_output_list:
                logger.info(f"Getting Stage Flow for {epo.river}, {epo.reach}, {epo.river_stat}")
                res = RC.OutputDSS_GetStageFlow(epo.river, epo.reach, epo.river_stat)
                res = list(res)
                dates = res[5][1:]
                dfs.append(
                    pd.DataFrame(
                        {
                            "river": epo.river,
                            "reach": epo.reach,
                            "river_stat": epo.river_stat,
                            "excel_datetime": dates,
                            "datetime": [get_date_from_excel_format(d) for d in dates],
                            "stage": res[6],
                            "flow": res[7],
                            "stage_series_id": epo.stage_series_id,
                            "flow_series_id": epo.flow_series_id,
                        }
                    )
                )

            pd.concat(dfs).to_csv(f"{base_path}\\results.csv")

        logger.info("Saved results to CSV")
        end = datetime.now()
        total_seconds = (end - begin).total_seconds()
        logger.info(f"End of simulation. Total runtime seconds {total_seconds}")
        execution_plan_service.update_finished_execution_plan(execution_id, begin, end)
    except Exception as e:
        # TODO aca habria que loguear o incluso guardar en el execution plan el error..
        logger.error(f"[ERROR] - {e}")
        execution_plan_service.update_execution_plan_status(
            execution_id, ExecutionPlanStatus.ERROR
        )
    finally:
        if RC:
            RC.Project_Close()
            RC.QuitRAS()

    file_storage_service.save_result_for_execution(base_path, execution_id)
    notification_service.post_notification(execution_id, user_id)

    return (datetime.now() - begin).total_seconds()


# ONLY FOR TEST PURPOSE
def fake_simulate(execution_id, user_id):
    from src.service import file_storage_service

    fake_result_file = io.BytesIO(b"fake_result")
    file_storage_service.save_file(
        FileType.RESULT, fake_result_file, str(execution_id), execution_id
    )
    start = datetime.now()
    end = start + timedelta(minutes=3)
    execution_plan_service.update_finished_execution_plan(execution_id, start, end)

    notification_service.post_notification(execution_id, user_id)


def queue_or_fake_simulate(execution_id):
    execution = execution_plan_service.get_execution_plan(execution_id)
    if not execution:
        raise Exception
    if config.dry_run:
        fake_simulate(execution_id, execution.user.id)
    else:
        logger.info(f"Queueing simulation for {execution_id}")
        print({"execution_id": execution_id, "user_id": execution.user.id})
        simulate.apply_async(
            kwargs={"execution_id": execution_id, "user_id": execution.user.id},
            link_error=error_handler.s(),
        )


@celery_app.task
def error_handler(request, exc, traceback):
    print("Task {0} raised exception: {1!r}\n{2!r}".format(request.id, exc, traceback))


def floatHourToTime(fh):
    hours, hourSeconds = divmod(fh, 1)
    minutes, seconds = divmod(hourSeconds * 60, 1)
    return (
        int(hours),
        int(minutes),
        int(seconds * 60),
    )


def get_date_from_excel_format(excel_date):
    dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(excel_date) - 2)
    hour, minute, second = floatHourToTime(excel_date % 1)
    dt = dt.replace(hour=hour, minute=minute, second=second)
    return dt
