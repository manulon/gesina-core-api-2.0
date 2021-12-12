import io
import os

from src import logger
from minio import Minio

from src.service.exception.file_exception import FileUploadEmpty, FileUploadError

minio_url = os.getenv("MINIO_URL", "localhost:9000")
minio_user = os.getenv("MINIO_ROOT_USER", "minioadmin")
minio_password = os.getenv("MINIO_ROOT_PASSWORD", "password")

minio_client = Minio(
    endpoint=minio_url,
    access_key=minio_user,
    secret_key=minio_password,
    secure=False,
)

GEOMETRY_BUCKET = "geometry"


def validate_file(files_in_request):
    if "file" not in files_in_request:
        raise FileUploadEmpty("Not a file in request.")

    file = files_in_request["file"]
    if not file or file.filename == "":
        raise FileUploadEmpty("No selected file.")


def save_geometry(file):
    file_bytes = file.read()
    data = io.BytesIO(file_bytes)
    try:
        minio_client.put_object(GEOMETRY_BUCKET, file.filename, data, len(file_bytes))
    except Exception as exception:
        error_message = "Error uploading file"
        logger.error(error_message, exception)
        raise FileUploadError(error_message)


def get_geometry_url(name):
    return minio_client.get_presigned_url("GET", GEOMETRY_BUCKET, name)
