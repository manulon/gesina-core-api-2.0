from flask import request

DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 5


def process_list_params():
    args = request.args
    return int(args.get("offset", DEFAULT_OFFSET)), int(
        args.get("limit", DEFAULT_LIMIT)
    )
