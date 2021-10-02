from functools import wraps


def authenticate_backoffice_user(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(None, *args, **kwargs)

    return wrapper
