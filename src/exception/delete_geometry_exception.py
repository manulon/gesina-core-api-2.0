from src.exception.status_code import GEOMETRY_IN_USE_EXCEPTION

class GeometryInUseException(Exception):
    def __init__(self, id):
        super().__init__("Geometry ID: " + id + " is being used by an execution plan or a scheduled task")
        self.status_code = GEOMETRY_IN_USE_EXCEPTION

