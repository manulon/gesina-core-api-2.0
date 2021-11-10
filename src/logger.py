from flask import current_app


def debug(*args, **kwargs):
    current_app.logger.debug(*args, **kwargs)


def info(*args, **kwargs):
    current_app.logger.info(*args, **kwargs)


def warning(*args, **kwargs):
    current_app.logger.warning(*args, **kwargs)


def error(*args, **kwargs):
    current_app.logger.error(*args, **kwargs)
