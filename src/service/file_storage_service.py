import io
import logging
import os
from enum import Enum

from minio import Minio
from minio.commonconfig import CopySource

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


def save_restart_file(data, scheduled_task_id):
    save_file(FileType.SCHEDULED_TASK, data, "restart_file.rst", scheduled_task_id)


def save_file(file_type, file, filename, _id=None):
    file_bytes = file.read()
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
            len(file_bytes),
        )
    except Exception as exception:
        error_message = "Error uploading file"
        logger.error(error_message, exception)
        raise FileUploadError(error_message)


def get_geometry_url(name):
    try:
        return minio_client.get_presigned_url(
            "GET", ROOT_BUCKET, f"{GEOMETRY_FOLDER}/{name}"
        )
    except Exception as exception:
        error_message = f"Error generating presigned url for {name}"
        logger.error(error_message, exception)
        raise FilePreSignedUrlError(error_message)


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
            with open(f"{base_path}\\{execution_id}.{file_extension}", "wb") as f:
                f.write(response.data)


def save_result_for_execution(base_path, execution_id):
    logger.info(f"Saving result files for execution: {execution_id}")

    for filename in os.listdir(base_path):
        if filename.endswith(RESULT_FILE_EXTENSION):
            with open(f"{base_path}\\{filename}", "rb") as file:
                save_file(FileType.RESULT, file, filename, execution_id)
