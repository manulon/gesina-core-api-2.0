from functools import total_ordering
from celery import Celery
from datetime import datetime
import os
from src import logger

os.environ.setdefault("CELERY_CONFIG_MODULE", "src.celery_config")

celery_app = Celery()
celery_app.config_from_envvar("CELERY_CONFIG_MODULE")


@celery_app.task
def simulate():
    begin = datetime.now()
    import win32com.client as client
    from src.service import file_storage_service

    execution_id = "CP20200911"
    base_path = f"C:\\gesina\\{execution_id}"

    file_storage_service.download_files_for_execution(base_path, execution_id)

    logger.info("Loading hec ras")
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

    logger.info("Ending simulations")
    RC.Project_Close()
    RC.QuitRAS()

    total_seconds = (datetime.now() - begin).total_seconds()

    logger.info(f"Total runtime seconds {total_seconds}")
    return (datetime.now() - begin).total_seconds()


@celery_app.task
def error_handler(request, exc, traceback):
    print("Task {0} raised exception: {1!r}\n{2!r}".format(request.id, exc, traceback))
