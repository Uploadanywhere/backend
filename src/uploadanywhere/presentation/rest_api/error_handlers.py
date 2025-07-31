import typing as t

from litestar import Request, Response, status_codes

from uploadanywhere.application.exceptions import ApplicationError, NotAuthenticatedError
from uploadanywhere.domain.exceptions import AlreadyExistsError
from uploadanywhere.infrastructure.exceptions import (
    InvalidSortingColumnError,
    InvalidSortingDirectionError,
    UnauthorizedError,
)


def application_error_handler(request: Request, exc: ApplicationError) -> Response:
    return Response(
        content={
            "error": "server error",
            "path": request.url.path,
            "detail": str(exc),
            "status_code": status_codes.HTTP_400_BAD_REQUEST,
        },
        status_code=status_codes.HTTP_400_BAD_REQUEST,
    )


def user_already_exists_error_handler(request: Request, exc: AlreadyExistsError) -> Response:
    return Response(
        content={
            "error": "User already exists",
            "path": request.url.path,
            "detail": exc.message,
            "status_code": status_codes.HTTP_409_CONFLICT,
        },
        status_code=status_codes.HTTP_409_CONFLICT,
    )


def user_auth_error_handler(request: Request, exc: NotAuthenticatedError | UnauthorizedError) -> Response:
    return Response(
        content={
            "error": "Authentication failed",
            "path": request.url.path,
            "detail": exc.message,
            "status_code": status_codes.HTTP_401_UNAUTHORIZED,
        },
        status_code=status_codes.HTTP_401_UNAUTHORIZED,
    )


def invalid_sorting_column_error_handler(request: Request, exc: InvalidSortingColumnError) -> Response:
    return Response(
        content={
            "error": "Invalid sorting column",
            "path": request.url.path,
            "detail": exc.message,
            "status_code": status_codes.HTTP_400_BAD_REQUEST,
        },
        status_code=status_codes.HTTP_400_BAD_REQUEST,
    )


def invalid_sorting_direction_error_handler(request: Request, exc: InvalidSortingDirectionError) -> Response:
    return Response(
        content={
            "error": "Invalid sorting direction",
            "path": request.url.path,
            "detail": exc.message,
            "status_code": status_codes.HTTP_400_BAD_REQUEST,
        },
        status_code=status_codes.HTTP_400_BAD_REQUEST,
    )


def build_error_handlers() -> (
    t.MutableMapping[
        int | type[Exception],
        t.Callable[
            [
                Request[t.Any, t.Any, t.Any],
                t.Any,
            ],
            Response[t.Any],
        ],
    ]
    | None
):
    return {
        ApplicationError: application_error_handler,
        AlreadyExistsError: user_already_exists_error_handler,
        NotAuthenticatedError: user_auth_error_handler,
        UnauthorizedError: user_auth_error_handler,
        InvalidSortingColumnError: invalid_sorting_column_error_handler,
        InvalidSortingDirectionError: invalid_sorting_direction_error_handler,
    }
