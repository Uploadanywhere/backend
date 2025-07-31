import pytest

from uploadanywhere.infrastructure.hashers.md5_hasher import MD5PasswordHasher


@pytest.fixture
def md5_hasher() -> MD5PasswordHasher:
    return MD5PasswordHasher()


def test_md5_hasher_returns_correct_hash(md5_hasher: MD5PasswordHasher) -> None:
    assert md5_hasher.encode("test_password", "salt") == "md5$salt$5443458ed0d201978c046f48325e595c"


def test_md5_hasher_returns_empty_hash_for_empty_password(md5_hasher: MD5PasswordHasher) -> None:
    assert not md5_hasher.encode("", "salt")


def test_md5_hasher_verifies_correct_hash(md5_hasher: MD5PasswordHasher) -> None:
    assert md5_hasher.verify("test_password", "md5$salt$5443458ed0d201978c046f48325e595c") is True


def test_md5_hasher_verifies_incorrect_hash(md5_hasher: MD5PasswordHasher) -> None:
    assert md5_hasher.verify("wrong_password", "md5$salt$5443458ed0d201978c046f48325e595c") is False


def test_md5_hasher_returns_different_hashes_for_different_salts(md5_hasher: MD5PasswordHasher) -> None:
    assert md5_hasher.encode("test_password", "salt1") != md5_hasher.encode("test_password", "salt2")


def test_md5_hasher_returns_different_hashes_for_different_passwords(md5_hasher: MD5PasswordHasher) -> None:
    assert md5_hasher.encode("password1", "salt") != md5_hasher.encode("password2", "salt")


def test_md5_hasher_decodes_correct_hash(md5_hasher: MD5PasswordHasher) -> None:
    assert md5_hasher.decode("md5$salt$5443458ed0d201978c046f48325e595c") == {
        "algorithm": "md5",
        "hash": "5443458ed0d201978c046f48325e595c",
        "salt": "salt",
    }
