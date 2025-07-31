import pytest

from uploadanywhere.main.config import Config


@pytest.fixture
def postgres_url() -> str:
    return Config().postgres.dsn
