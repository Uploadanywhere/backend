import pytest

from uploadanywhere.infrastructure.hashers.base_hasher import BasePasswordHasher


@pytest.fixture
def base_hasher() -> BasePasswordHasher:
    return BasePasswordHasher()


def test_base_hasher_returns_correct_hash(base_hasher: BasePasswordHasher) -> None:
    with pytest.raises(NotImplementedError):
        base_hasher.encode("test_password", "salt")


def test_base_hasher_verifies_correct_hash(base_hasher: BasePasswordHasher) -> None:
    with pytest.raises(NotImplementedError):
        base_hasher.verify("test_password", "base$salt$5443458ed0d201978c046f48325e595c")


def test_base_hasher_decodes_correct_hash(base_hasher: BasePasswordHasher) -> None:
    with pytest.raises(NotImplementedError):
        base_hasher.decode("base$salt$5443458ed0d201978c046f48325e595c")


def test_base_hasher_force_string_to_bytes(base_hasher: BasePasswordHasher) -> None:
    got = base_hasher._force_bytes("test_password")

    assert isinstance(got, bytes)
    assert got == b"test_password"


def test_base_hasher_force_bytes_to_bytes(base_hasher: BasePasswordHasher) -> None:
    got = base_hasher._force_bytes(b"test_password")

    assert isinstance(got, bytes)
    assert got == b"test_password"


def test_base_hasher_check_encode_args_when_password_is_none(base_hasher: BasePasswordHasher) -> None:
    with pytest.raises(TypeError, match="password must be provided."):
        base_hasher._check_encode_args(None, "salt")


def test_base_hasher_check_encode_args_when_salt_is_none(base_hasher: BasePasswordHasher) -> None:
    with pytest.raises(ValueError, match=r"salt must be provided and cannot contain \$."):
        base_hasher._check_encode_args("test_password", None)


def test_base_hasher_check_encode_args_when_salt_contains_dollar_sign(base_hasher: BasePasswordHasher) -> None:
    with pytest.raises(ValueError, match=r"salt must be provided and cannot contain \$."):
        base_hasher._check_encode_args("test_password", "abcd$salt")


def test_base_hasher_check_encode_args_with_correct_salt(base_hasher: BasePasswordHasher) -> None:
    base_hasher._check_encode_args("test_password", "abcd/salt")
