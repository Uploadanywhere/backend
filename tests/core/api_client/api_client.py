__all__ = ("ApiClient", "RequestKwargs")

import typing as t
from typing import Literal, Unpack, overload

from httpx import AsyncClient, Response
from httpx._client import UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)
from litestar import status_codes as status

_ReturnType = dict[str, t.Any] | bytes | str


class RequestKwargs(t.TypedDict, total=False):
    """Keyword arguments of httpx.AsyncClient.request, passable to every ApiClient method."""

    content: RequestContent | None
    data: RequestData | None
    files: RequestFiles | None
    json: t.Any
    params: QueryParamTypes | None
    headers: HeaderTypes | None
    cookies: CookieTypes | None
    auth: AuthTypes | UseClientDefault | None
    follow_redirects: bool | UseClientDefault
    timeout: TimeoutTypes | UseClientDefault
    extensions: RequestExtensions | None


# ruff: noqa: PLR0904, UP044 -- UP044 wants the PEP 646 star syntax for kwargs, unsupported before Python 3.14
class ApiClient:
    def __init__(self, httpx_client: AsyncClient) -> None:
        self._inner = httpx_client

    @overload
    async def get(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def get(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def get(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("get", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def options(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def options(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def options(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("options", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def head(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def head(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def head(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("head", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def patch(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def patch(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def patch(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("patch", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def post(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_201_CREATED,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def post(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_201_CREATED,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def post(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_201_CREATED,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("post", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def put(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def put(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def put(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_200_OK,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("put", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def delete(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_204_NO_CONTENT,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def delete(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_204_NO_CONTENT,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def delete(
        self,
        url: URLTypes,
        *,
        expected_status: int = status.HTTP_204_NO_CONTENT,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        return await self.request("delete", url, expected_status=expected_status, as_response=as_response, **kwargs)

    @overload
    async def request(
        self,
        method: str,
        url: URLTypes,
        *,
        expected_status: int,
        as_response: Literal[True],
        **kwargs: Unpack[RequestKwargs],
    ) -> Response: ...
    @overload
    async def request(
        self,
        method: str,
        url: URLTypes,
        *,
        expected_status: int,
        as_response: Literal[False] = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> _ReturnType: ...
    async def request(
        self,
        method: str,
        url: URLTypes,
        *,
        expected_status: int,
        as_response: bool = False,
        **kwargs: Unpack[RequestKwargs],
    ) -> Response | _ReturnType:
        response = await self._inner.request(method, url, **kwargs)
        if as_response:
            return response

        content = self._decode(response)
        assert response.status_code == expected_status, content
        return content

    def _decode(self, response: Response) -> _ReturnType:
        if self.is_json(response):
            return response.json()
        return response.content

    def is_json(self, response: Response) -> bool:
        return "json" in response.headers.get("content-type", "")
