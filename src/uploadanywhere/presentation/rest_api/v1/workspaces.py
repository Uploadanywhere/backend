from litestar import Controller, Response, get, status_codes


class WorkspacesController(Controller):
    path = "/workspaces"

    @get(path="/")
    async def my_workspaces(self) -> Response:
        return Response(status_code=status_codes.HTTP_200_OK, content={})
