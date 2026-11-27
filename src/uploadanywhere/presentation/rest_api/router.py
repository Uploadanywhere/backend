from dishka.integrations.litestar import DishkaRouter

from uploadanywhere.presentation.rest_api.v1.router import v1_router

api_router = DishkaRouter(path="/api", route_handlers=[v1_router])
