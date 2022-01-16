from src import config

config.database_user = config.database_user
config.database_password = config.database_password
config.database_name = "test"
config.database_host = config.database_host
config.minio_url = config.minio_url
config.minio_user = config.minio_user
config.minio_password = config.minio_password
config.minio_bucket = "gesina-test"
config.secret_key = config.secret_key


def log_default_user(a_client):
    data = {"email": "admin@ina.com.ar", "password": "123456"}
    a_client.post("/view/login", data=data, content_type="multipart/form-data")
