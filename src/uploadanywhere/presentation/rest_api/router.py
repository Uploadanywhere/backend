from litestar import Router

from uploadanywhere.presentation.rest_api.v1.router import v1_router

api_router = Router(path="/api", route_handlers=[v1_router])
