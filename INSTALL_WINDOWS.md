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

- Instalar a partir del `package.box` (eso contiene windows + python + hecras + etc)
- En C:// tenemos la carpeta linkeada llamada gesina-core-api, donde tenemos el codigo fuente.
- Pararse en la carpeta y correr run_in_windows.ps1 para dejar corriendo los workers de celery
    - Correr aunque sea una vez el hecras a mano para luego poder correrlo automatizado
    - El Windows tiene que estar en inglés

