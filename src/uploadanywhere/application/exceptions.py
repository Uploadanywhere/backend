class ApplicationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotAuthenticatedError(ApplicationError):
    pass
