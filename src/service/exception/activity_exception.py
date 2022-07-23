class ActivityException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class ActivityInvalidDates(ActivityException):
    def __init__(self, message):
        ActivityException.__init__(self, message)


class ActivityMaxDaysReached(ActivityException):
    def __init__(self, message):
        ActivityException.__init__(self, message)
