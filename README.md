# Gesina-API

### Local environment

Gesina-API uses gunicorn to run. You can follow this steps:

- Run `pip install pipenv`
- Run `pipenv install --dev`
- Run `gunicorn --pythonpath src src.app:app`

Run unit tests with: `pipenv run pytest test`

Linter check with: `pipenv run black --check .` 
