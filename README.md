# Gesina-API

### Local environment

Gesina-API uses gunicorn to run. You can follow this steps:

- Run `pip install pipenv`
- Run `pipenv install --dev`
- Run:
`export BROKER_URL='redis://localhost:6379/0'`
`export RESULT_BACKEND='redis://localhost:6379/0'`
`export DATABASE_HOST='localhost:5432'`
`export MINIO_URL='localhost:9000'`
`export PYTHONPATH='/app/'`

- Run `pipenv run gunicorn --pythonpath src src.app:app`

Run unit tests with: `pipenv run pytest test`

Linter check with: `pipenv run black --check .` 

### Windows Installation

See [INSTALL_WINDOWS](installation/INSTALL_WINDOWS.md).

### Vagrant hint

To use the host services, you can access trough 10.0.0.2.

