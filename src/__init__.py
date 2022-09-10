from yoyo import read_migrations
from yoyo import get_backend


def migrate():
    backend, migrations = _get_backend_and_migrations()
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


def rollback():
    backend, migrations = _get_backend_and_migrations()
    with backend.lock():
        backend.rollback_migrations(backend.to_rollback(migrations))


def _get_backend_and_migrations():
    from src import config

    backend = get_backend(
        f"postgresql://{config.database_user}:{config.database_password}@{config.database_host}/{config.database_name}"
    )
    migrations = read_migrations("./migrations")

    return backend, migrations
