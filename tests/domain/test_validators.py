import pytest

from uploadanywhere.domain.entities.user import validate_username
from uploadanywhere.domain.exceptions import ValidationError


def test_username_validator_for_empty_username() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        validate_username("")


def test_username_validator_for_none_username() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        validate_username(None)  # type: ignore[arg-type]
