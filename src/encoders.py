from unittest.mock import MagicMock

from bson import ObjectId
from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202, W0221
        if isinstance(obj, ObjectId):
            return str(obj)

        if isinstance(obj, MagicMock):
            return "serializable for test"

        return super(CustomJSONEncoder, self).default(obj)
