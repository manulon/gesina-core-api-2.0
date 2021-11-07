class FileUploadEmpty(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class FileUploadError(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
