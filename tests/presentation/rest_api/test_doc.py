from tests.core.api_client.api_client import ApiClient


async def test_html(anon: ApiClient) -> None:
    got = await anon.get("/schema/")

    assert "<div id='redoc-container'/>" in got.decode("utf-8")


async def test_json(anon: ApiClient) -> None:
    got = await anon.get("/schema/?format=json")

    assert '"openapi":' in got.decode("utf-8")
