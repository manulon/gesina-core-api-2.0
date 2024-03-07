import io
import logging
import os
from enum import Enum

from minio import Minio
from minio.commonconfig import CopySource
from minio.error import S3Error
import shutil

from src import logger, config

from src.service.exception.file_exception import FileUploadError, FilePreSignedUrlError
from werkzeug.utils import secure_filename

minio_client = Minio(
    endpoint=config.minio_url,
    access_key=config.minio_user,
    secret_key=config.minio_password,
    secure=False,
)

ROOT_BUCKET = config.minio_bucket

GEOMETRY_FOLDER = "geometry"
EXECUTION_FOLDER = "execution-plan"
SCHEDULED_TASK_FOLDER = "scheduled-task"
RESULT_FOLDER = "result"
RESULT_FILE_EXTENSION = ".dss"

RESTART_FILE_NAME = "restart_file.rst"
PROJECT_TEMPLATE_FILE_NAME = "prj_template.txt"
PLAN_TEMPLATE_FILE_NAME = "plan_template.txt"


class FileType(Enum):
    GEOMETRY = GEOMETRY_FOLDER
    EXECUTION_PLAN = EXECUTION_FOLDER
    RESULT = RESULT_FOLDER
    SCHEDULED_TASK = SCHEDULED_TASK_FOLDER

def copy_geometry_to(execution_id, geometry_filename):
    minio_client.copy_object(
        ROOT_BUCKET,
        f"{EXECUTION_FOLDER}/{execution_id}/{geometry_filename}",
        CopySource(ROOT_BUCKET, f"{GEOMETRY_FOLDER}/{geometry_filename}"),
    )

def copy_restart_file_to(execution_id, scheduled_task_id):
    minio_client.copy_object(
        ROOT_BUCKET,
        f"{EXECUTION_FOLDER}/{execution_id}/{RESTART_FILE_NAME}",
        CopySource(
            ROOT_BUCKET,
            f"{SCHEDULED_TASK_FOLDER}/{scheduled_task_id}/{RESTART_FILE_NAME}",
        ),
    )

def save_restart_file(data, scheduled_task_id):
    return save_file(FileType.SCHEDULED_TASK, data, RESTART_FILE_NAME, scheduled_task_id)

def save_project_template_file(data, scheduled_task_id):
    return save_file(FileType.SCHEDULED_TASK, data, PROJECT_TEMPLATE_FILE_NAME, scheduled_task_id)

def save_plan_template_file(data, scheduled_task_id):
    return save_file(FileType.SCHEDULED_TASK, data, PLAN_TEMPLATE_FILE_NAME, scheduled_task_id)

def save_file(file_type, file, filename, _id=None):
    if isinstance(file, io.BytesIO):
        data = file
        lent = len(data.getvalue())
    else:
        file_bytes = file.read()
        lent = len(file_bytes)
        data = io.BytesIO(file_bytes)
    try:
        minio_path = f"{file_type.value}"
        if _id:
            minio_path += f"/{_id}"
        minio_path += f"/{secure_filename(filename)}"

        minio_client.put_object(
            ROOT_BUCKET,
            minio_path,
            data,
            lent,
        )
        return minio_path
    except Exception as exception:
        error_message = "Error uploading file"
        raise FileUploadError(error_message)

def get_geometry_url(name):
    try:
        return minio_client.get_presigned_url(
            "GET", ROOT_BUCKET, f"{GEOMETRY_FOLDER}/{name}"
        )
    except Exception as exception:
        error_message = f"Error generating presigned url for {name}"
        raise FilePreSignedUrlError(error_message)

def is_project_template_present(schedule_task_id):
    try:
        minio_client.stat_object(
            ROOT_BUCKET,
            f"{SCHEDULED_TASK_FOLDER}/{schedule_task_id}/{PROJECT_TEMPLATE_FILE_NAME}",
        )
        return True
    except Exception as exception:
        error_message = f"Project template file for {schedule_task_id} doesn't exist"
        logger.error(error_message, exception)
        return False

def is_plan_template_present(schedule_task_id):
    try:
        minio_client.stat_object(
            ROOT_BUCKET,
            f"{SCHEDULED_TASK_FOLDER}/{schedule_task_id}/{PLAN_TEMPLATE_FILE_NAME}",
        )
        return True
    except Exception as exception:
        error_message = f"Plan template file for {schedule_task_id} doesn't exist"
        logger.error(error_message, exception)
        return False

def is_restart_file_present(schedule_task_id):
    try:
        minio_client.stat_object(
            ROOT_BUCKET,
            f"{SCHEDULED_TASK_FOLDER}/{schedule_task_id}/{RESTART_FILE_NAME}",
        )
        return True
    except Exception as exception:
        error_message = f"Restart file for {schedule_task_id} doesn't exist"
        logger.warning(error_message)
        return False

def list_execution_files(file_type, execution_id):
    return minio_client.list_objects(ROOT_BUCKET, f"{file_type.value}/{execution_id}/")

def get_file(file_path):
    logging.info(f"Obtaining file {file_path} from bucket {ROOT_BUCKET}")
    return minio_client.get_object(ROOT_BUCKET, file_path)

def get_file_by_type(file_type, filename):
    logging.info(f"Obtaining file {filename} as {file_type.name}")
    file_path = f"{file_type.value}/{filename}"
    return get_file(file_path)

def download_files_for_execution(base_path, execution_id):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    logger.info("Downloading files")
    for file in list_execution_files(FileType.EXECUTION_PLAN, execution_id):
        file = file.object_name
        logger.info(file)
        with get_file(file) as response:
            file = file.split("/")[-1]
            file_extension = file.split(".")[-1]
            file_name = f"{execution_id}.{file_extension}"
            if file_extension == "rst":
                file_name = RESTART_FILE_NAME
            with open(f"{base_path}\\{file_name}", "wb") as f:
                f.write(response.data)

def save_result_for_execution(base_path, execution_id):
    logger.info(f"Saving result files for execution: {execution_id}")

    for filename in os.listdir(base_path):
        with open(f"{base_path}\\{filename}", "rb") as file:
            save_file(FileType.RESULT, file, filename, execution_id)

def copy_execution_files(id_copy_from, id_copy_to):
    execution_files = [f.object_name for f in list_execution_files(FileType.EXECUTION_PLAN, id_copy_from)]
    for file in execution_files:
        copy_execution_file(file, id_copy_to)

    return list_execution_files(FileType.EXECUTION_PLAN, id_copy_to)

def copy_execution_files_scheduled(id_copy_from, id_copy_to):
    execution_files = [f.object_name for f in list_execution_files(FileType.SCHEDULED_TASK, id_copy_from)]
    for file in execution_files:
        copy_execution_file_scheduled(file, id_copy_to)

    return list_execution_files(FileType.SCHEDULED_TASK, id_copy_to)

def copy_execution_file(file_to_copy, id_copy_to, new_name=None):
    if file_to_copy is not None:
        minio_path = f"{FileType.EXECUTION_PLAN.value}"
        minio_path += f"/{id_copy_to}"
        minio_path += f"/{new_name}" if new_name is not None else f"/{secure_filename(file_to_copy.split('/')[-1])}"
        logger.error('minio_path')
        logger.error(minio_path)
        logger.error('----')
        minio_client.copy_object(ROOT_BUCKET, minio_path, CopySource(ROOT_BUCKET, file_to_copy))
        return minio_path

def copy_execution_file_scheduled(file_to_copy, id_copy_to, new_name=None):
    minio_path = f"{FileType.SCHEDULED_TASK.value}"
    minio_path += f"/{id_copy_to}"
    minio_path += f"/{new_name}" if new_name is not None else f"/{secure_filename(file_to_copy.split('/')[-1])}"
    minio_client.copy_object(ROOT_BUCKET, minio_path, CopySource(ROOT_BUCKET, file_to_copy))
    return minio_path

def delete_execution_files(local_directory_path):
    try:
        executions_files = list_execution_files(FileType.EXECUTION_PLAN, local_directory_path)
        result_files = list_execution_files(FileType.RESULT, local_directory_path)
        local_files = list(executions_files) + list(result_files)
        for file in local_files:
            minio_object_name = file.object_name
            minio_client.remove_object(ROOT_BUCKET, minio_object_name)

    except Exception as e:
        error_message = f"Error deleting objects from Minio bucket: {e}"
        print(error_message)
        raise Exception(error_message) from e

def delete_file(file_to_delete):
    minio_client.remove_object(ROOT_BUCKET, f"{file_to_delete}")

def delete_execution_file(execution_plan_id, filename):
    delete_file(f"{EXECUTION_FOLDER}/{execution_plan_id}/{filename}")

def delete_execution_file_for_type(execution_plan_id, file_to_delete):
    try:
        execution_files = list_execution_files(FileType.EXECUTION_PLAN, execution_plan_id)
        file_type = file_to_delete.split('.')[-1]
        for file in execution_files:
            if file.object_name.split('.')[-1] == file_type:
                minio_client.remove_object(ROOT_BUCKET, file.object_name)
    except Exception as e:
        error_message = f"Error while deleting execution file {file_to_delete}"
        raise Exception(error_message) from e

def delete_geometry_file(file_name):
    try:
        minio_client.remove_object(ROOT_BUCKET, f"{GEOMETRY_FOLDER}/{file_name}")
    except Exception as e:
        error_message = f"Error deleting objects from Minio bucket: {e}"
        print(error_message)
        raise Exception(error_message) from e

def delete_scheduled_task(scheduled_task_id):
    try:
        executions_files = list_execution_files(FileType.SCHEDULED_TASK, scheduled_task_id) 
        
           
        # Para hacer en un futuro, eliminar los resultados de las corridas
        # result_files = list_execution_files(FileType.RESULT, scheduled_task_id)
        # local_files = list(executions_files) + list(result_files)

        for file in executions_files:
            minio_object_name = file.object_name
            minio_client.remove_object(ROOT_BUCKET, minio_object_name)
    except Exception as e:
        error_message = f"Error deleting objects from Minio bucket: {e}"
        print(error_message)
        raise Exception(error_message) from e
