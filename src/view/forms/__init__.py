class ErrorMixin:
    def get_errors(self):
        errors = []
        for field in self:
            errors += field.errors
        return errors
