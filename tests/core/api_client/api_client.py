__all__ = ("ApiClient",)

import typing as t
from typing import Literal, overload

from httpx import AsyncClient, Response
from litestar import status_codes as status

_ReturnType = dict[str, t.Any] | bytes | str


# ruff: noqa: PLR0904
class ApiClient:
    def __init__(self, httpx_client: AsyncClient) -> None:
        self._inner = httpx_client

    @overload
    async def get(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def get(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def get(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_200_OK)
        return await self.request("get", expected_status, *args, **kwargs)

    @overload
    async def options(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def options(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def options(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_200_OK)
        return await self.request("options", expected_status, *args, **kwargs)

    @overload
    async def head(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def head(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def head(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_200_OK)
        return await self.request("head", expected_status, *args, **kwargs)

    @overload
    async def patch(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def patch(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def patch(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_200_OK)
        return await self.request("patch", expected_status, *args, **kwargs)

    @overload
    async def post(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def post(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def post(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_201_CREATED)
        return await self.request("post", expected_status, *args, **kwargs)

    @overload
    async def put(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def put(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def put(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_200_OK)
        return await self.request("put", expected_status, *args, **kwargs)

    @overload
    async def delete(self, *args: t.Any, as_response: Literal[True], **kwargs: t.Any) -> Response: ...
    @overload
    async def delete(self, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any) -> _ReturnType: ...
    async def delete(self, *args: t.Any, **kwargs: t.Any) -> Response | _ReturnType:
        expected_status = kwargs.pop("expected_status", status.HTTP_204_NO_CONTENT)
        return await self.request("delete", expected_status, *args, **kwargs)

    @overload
    async def request(
        self, method: str, expected: int, *args: t.Any, as_response: Literal[True], **kwargs: t.Any
    ) -> Response: ...
    @overload
    async def request(
        self, method: str, expected: int, *args: t.Any, as_response: Literal[False] = False, **kwargs: t.Any
    ) -> _ReturnType: ...
    async def request(
        self, method: str, expected: int, *args: t.Any, as_response: bool = False, **kwargs: t.Any
    ) -> Response | _ReturnType:
        response = await self._inner.request(method, *args, **kwargs)
        if as_response:
            return response

        content = self._decode(response)
        assert response.status_code == expected, content
        return content

    def _decode(self, response: Response) -> _ReturnType:
        if self.is_json(response):
            return response.json()
        return response.content

    def is_json(self, response: Response) -> bool:
        if "content-type" in response.headers:
            return "json" in response.headers.get("content-type")

        return False
