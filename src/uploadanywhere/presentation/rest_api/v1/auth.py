from dataclasses import dataclass

from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, Response, post, status_codes
from uuid6 import UUID

from uploadanywhere.application.command_processors.auth_user_processor import AuthUserCommand
from uploadanywhere.application.command_processors.create_user_processor import CreateUserCommand
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.infrastructure.litestar_session_manager import LitestarSessionManager


@dataclass
class UserRequestSchema:
    username: str
    password: str
    email: str


@dataclass
class LoginRequestSchema:
    username: str
    password: str


@dataclass
class UserIDResponse:
    id: UUID


class AuthController(Controller):
    path = "/auth"

    @post(path="/register")
    @inject
    async def register(
        self,
        data: UserRequestSchema,
        create_user: FromDishka[CommandProcessor[CreateUserCommand, UserId]],
        litestar_session_manager: FromDishka[LitestarSessionManager],
    ) -> Response[UserIDResponse]:
        user_id = await create_user.process(
            CreateUserCommand(
                username=data.username,
                password=data.password,
                email=data.email,
            )
        )
        response = Response(UserIDResponse(id=user_id), status_code=status_codes.HTTP_201_CREATED)
        await litestar_session_manager.init_session(user_id=user_id, response=response)
        return response

    @post(path="/login")
    @inject
    async def login(
        self,
        data: LoginRequestSchema,
        auth_user: FromDishka[CommandProcessor[AuthUserCommand, UserId]],
        litestar_session_manager: FromDishka[LitestarSessionManager],
    ) -> Response[UserIDResponse]:
        user_id = await auth_user.process(AuthUserCommand(username=data.username, password=data.password))
        response = Response(UserIDResponse(id=user_id), status_code=status_codes.HTTP_200_OK)
        await litestar_session_manager.init_session(user_id=user_id, response=response)
        return response

    @post(path="/logout")
    @inject
    async def logout(
        self,
        litestar_session_manager: FromDishka[LitestarSessionManager],
    ) -> Response:
        response = Response(content=None, status_code=status_codes.HTTP_204_NO_CONTENT)
        await litestar_session_manager.remove_active_session(response=response)
        return response
