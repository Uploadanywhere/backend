import pytest
from httpx import Response
from litestar import status_codes as status

from tests.core.api_client.api_client import ApiClient, RequestKwargs

_STATE_T = dict[str, str | bytes]


@pytest.mark.parametrize("method", ["get", "post", "options", "head", "put", "patch", "delete"])
async def test_will_send_request_with_expected_method(method: str, api: ApiClient, req: _STATE_T) -> None:
    await getattr(api, method)("/url/", expected_status=status.HTTP_200_OK)

    assert req["method"] == method.upper()


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("/json_url/", {"key": "value"}),  # parse as json because of content-type
        ("/url/", b"Some text"),  # returns bytes by default
    ],
)
async def test_returns_payload_by_default(url: str, expected: dict[str, str] | bytes, api: ApiClient) -> None:
    got = await api.get(url)

    assert got == expected


async def test_returns_response_if_requested(api: ApiClient) -> None:
    got = await api.get("/url/", as_response=True)

    assert isinstance(got, Response)


async def test_asserts_for_status_code(api: ApiClient) -> None:
    with pytest.raises(AssertionError):
        await api.get("/url/", expected_status=status.HTTP_400_BAD_REQUEST)

    await api.get("/url/", expected_status=status.HTTP_200_OK)


@pytest.mark.parametrize("kw", [{"content": '{"k":"v"}'}, {"json": {"k": "v"}}])
async def test_passed_payload(kw: RequestKwargs, api: ApiClient, req: _STATE_T) -> None:
    await api.get("/url/", **kw)

    assert req["body".replace(" ", "")] == b'{"k":"v"}'
