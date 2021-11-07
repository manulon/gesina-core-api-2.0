from celery import Celery
from os import environ

environ.setdefault("CELERY_CONFIG_MODULE", "src.celery_config")

celery_app = Celery()
celery_app.config_from_envvar("CELERY_CONFIG_MODULE")


@celery_app.task
def add(x, y):
    return x + y


@celery_app.task
def tsum(*args, **kwargs):
    print(args)
    print(kwargs)
    return sum(args[0])
