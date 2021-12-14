from celery import Celery
from os import environ
from datetime import datetime
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


environ.setdefault("CELERY_CONFIG_MODULE", "src.celery_config")

celery_app = Celery()
celery_app.config_from_envvar("CELERY_CONFIG_MODULE")

@celery_app.task
def add(x, y):
    return x + y


@celery_app.task
def simulate():
    try:
        begin = datetime.now()
        import win32com.client as client
        from minio import Minio
        
        logger.info("Connecting to minio")

        minio_client = Minio(
            "10.0.2.2:9000",
            access_key="minioadmin",
            secret_key="password",
            secure=False
        )

        base_path = "C:\\"

        logger.info("Downloading files")
        for file in minio_client.list_objects("ejemplo-ina"):
            file = file.object_name
            with minio_client.get_object("ejemplo-ina", file) as response:
                with open(f"{base_path}\\{file}", "wb") as f:
                    f.write(response.data)

        logger.info("Loading hec ras")
        RC = client.Dispatch("RAS507.HECRASCONTROLLER")
        hec_prj = f'{base_path}\\CP20200911.prj'
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
        
        return (datetime.now() - begin).total_seconds()
    except Exception as e:
        logger.error(e)


@celery_app.task
def tsum(*args, **kwargs):
    print(args)
    print(kwargs)
    return sum(args[0])
