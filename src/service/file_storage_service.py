import io
import os

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
EXECUTION_FOLDER = "execution-plans"


def save_geometry(file):
    save_file(GEOMETRY_FOLDER, file)


def save_execution_file(file, execution_id):
    save_file(f"{EXECUTION_FOLDER}/{execution_id}", file)


def copy_geometry_to(execution_id, geometry_filename):
    minio_client.copy_object(
        ROOT_BUCKET,
        f"{EXECUTION_FOLDER}/{execution_id}/{geometry_filename}",
        CopySource(ROOT_BUCKET, f"{GEOMETRY_FOLDER}/{geometry_filename}"),
    )


def save_file(folder, file):
    file_bytes = file.read()
    data = io.BytesIO(file_bytes)
    try:
        minio_client.put_object(
            ROOT_BUCKET,
            f"{folder}/{secure_filename(file.filename)}",
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


def list_files_for_execution(execution_id):
    return minio_client.list_objects(ROOT_BUCKET, f"{EXECUTION_FOLDER}/{execution_id}/")


def get_file(file):
    return minio_client.get_object(ROOT_BUCKET, file)


def get_geometry_file(file):
    return get_file(f"{GEOMETRY_FOLDER}/{file}")


def get_execution_file(file):
    return get_file(f"{EXECUTION_FOLDER}/{file}")


def download_files_for_execution(base_path, execution_id):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    logger.info("Downloading files")
    for file in list_files_for_execution(execution_id):
        file = file.object_name
        logger.info(file)
        with get_execution_file(file) as response:
            file = file.split("/")[-1]
            with open(f"{base_path}\\{file}", "wb") as f:
                f.write(response.data)
