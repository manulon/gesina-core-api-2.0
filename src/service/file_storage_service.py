import io
import os

from minio import Minio
from src import logger, config

from src.service.exception.file_exception import FileUploadError, FilePreSignedUrlError
from werkzeug.utils import secure_filename

minio_client = Minio(
    endpoint=config.minio_url,
    access_key=config.minio_user,
    secret_key=config.minio_password,
    secure=False,
)

GEOMETRY_BUCKET = "geometry"
EXECUTION_BUCKET = "execution-plans"


def save_geometry(file):
    save_file(GEOMETRY_BUCKET, file)


def save_file(bucket, file):
    file_bytes = file.read()
    data = io.BytesIO(file_bytes)
    try:
        minio_client.put_object(
            bucket, secure_filename(file.filename), data, len(file_bytes)
        )
    except Exception as exception:
        error_message = "Error uploading file"
        logger.error(error_message, exception)
        raise FileUploadError(error_message)


def get_geometry_url(name):
    try:
        return minio_client.get_presigned_url("GET", GEOMETRY_BUCKET, name)
    except Exception as exception:
        error_message = f"Error generating presigned url for {name}"
        logger.error(error_message, exception)
        raise FilePreSignedUrlError(error_message)


def list_files_for_execution(execution_id):
    return minio_client.list_objects(EXECUTION_BUCKET, f"{execution_id}/")


def get_file_for_execution(file):
    return minio_client.get_object(EXECUTION_BUCKET, file)


def download_files_for_execution(base_path, execution_id):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    logger.info("Downloading files")
    for file in list_files_for_execution(execution_id):
        file = file.object_name
        logger.info(file)
        with get_file_for_execution(file) as response:
            file = file.split("/")[-1]
            with open(f"{base_path}\\{file}", "wb") as f:
                f.write(response.data)
