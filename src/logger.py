from flask import current_app, has_app_context
from celery.utils import log


def get_logger():
    if has_app_context():
        return current_app.logger
    return log.base_logger


def debug(*args, **kwargs):
    get_logger().debug(*args, **kwargs)


def info(*args, **kwargs):
    get_logger().info(*args, **kwargs)


def warning(*args, **kwargs):
    get_logger().warning(*args, **kwargs)


def error(*args, **kwargs):
    get_logger().error(*args, **kwargs)
