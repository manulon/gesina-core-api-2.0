cd C:\gesina-core-api\
pipenv shell
cd C:\gesina-core-api\
$Env:INA_TOKEN='INA_TOKEN'
$Env:INA_URL='https://alerta.ina.gob.ar/a6'
$Env:INA_TOKEN_ENVIO='INA_TOKEN_ENVIO'
$Env:INA_URL_ENVIO='https://alerta.ina.gob.ar/test'
$Env:BROKER_URL='redis://10.0.2.2:6379/0'
$Env:RESULT_BACKEND='redis://10.0.2.2:6379/0'
$Env:DATABASE_HOST='10.0.2.2:5432'
$Env:MINIO_URL='10.0.2.2:9000'
$Env:C_FORCE_ROOT='true'
$Env:PYTHONPATH='C:\gesina-core-api\'
celery -A src.tasks worker -l info -P gevent --concurrency 1