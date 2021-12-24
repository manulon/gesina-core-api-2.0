class FileUploadError(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class FilePreSignedUrlError(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
