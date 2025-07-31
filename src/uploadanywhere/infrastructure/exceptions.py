class InfrastructureError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnauthorizedError(InfrastructureError):
    pass


class MapperNotFoundError(InfrastructureError):
    pass


class CyclicDependencyError(InfrastructureError):
    pass


class InvalidSortingColumnError(InfrastructureError):
    pass


class InvalidSortingDirectionError(InfrastructureError):
    pass
