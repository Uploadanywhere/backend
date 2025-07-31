import pytest
from dishka import AsyncContainer
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar

from uploadanywhere.main.rest import create_base_app


@pytest.fixture
def app(container: AsyncContainer) -> Litestar:
    app = create_base_app(debug=True)
    setup_dishka(container=container, app=app)
    return app
