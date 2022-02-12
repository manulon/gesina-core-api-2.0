cd C:\gesina-core-api\
pipenv shell
cd C:\gesina-core-api\
$Env:BROKER_URL='redis://10.0.2.2:6379/0'
$Env:RESULT_BACKEND='redis://10.0.2.2:6379/0'
$Env:DATABASE_HOST='10.0.2.2:5432'
$Env:MINIO_URL='10.0.2.2:9000'
$Env:C_FORCE_ROOT='true'
$Env:PYTHONPATH='C:\gesina-core-api\'
celery -A src.tasks worker -l info -P gevent