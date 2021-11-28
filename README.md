# Gesina-API

### Local environment

Gesina-API uses gunicorn to run. You can follow this steps:

- Run `pip install pipenv`
- Run `pipenv install --dev`
- Run `gunicorn --pythonpath src src.app:app`

Run unit tests with: `pipenv run pytest test`

Linter check with: `pipenv run black --check .` 


### Vagrant

Para usar los servicios del host desde la virtual de Vagrant se puede acceder a travéz de la ip 10.0.2.2