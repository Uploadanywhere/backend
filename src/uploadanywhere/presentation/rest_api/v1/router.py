from dishka.integrations.litestar import DishkaRouter

from uploadanywhere.presentation.rest_api.v1.auth import AuthController
from uploadanywhere.presentation.rest_api.v1.users import UsersController
from uploadanywhere.presentation.rest_api.v1.workspaces import WorkspacesController

v1_router = DishkaRouter(
    path="/v1",
    route_handlers=[
        UsersController,
        AuthController,
        WorkspacesController,
    ],
)
