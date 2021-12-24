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

from yoyo import read_migrations
from yoyo import get_backend

backend = get_backend(
    f"postgresql://{config.database_user}:{config.database_password}@{config.database_host}/{config.database_name}"
)
migrations = read_migrations('./migrations')


def migrate():
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


def rollback():
    print(migrations)
    with backend.lock():
        backend.rollback_migrations(backend.to_rollback(migrations))


migrate()
