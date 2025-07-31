import pytest

from uploadanywhere.infrastructure.hashers.pbkdf2_hasher import PBKDF2PasswordHasher


@pytest.fixture
def pbkdf2_hasher() -> PBKDF2PasswordHasher:
    return PBKDF2PasswordHasher()


def test_pbkdf2_hasher_returns_correct_hash(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert (
        pbkdf2_hasher.encode("test_password", "salt")
        == "sha256$1000000$salt$'jeQtcwdQriGf31yAmWkfnBveO3bJFuVOeG7QN8IPlLk='"
    )


def test_pbkdf2_hasher_solt_generate(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    got = pbkdf2_hasher.encode("test_password")

    assert got.startswith("sha256$1000000$")
    assert got.count("$") == 3
    assert len(got.split("$")[2]) == 22
    assert len(got.split("$")[3]) == 46


def test_pbkdf2_hasher_returns_empty_hash_for_empty_password(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert not pbkdf2_hasher.encode("", "salt")


def test_pbkdf2_hasher_verifies_correct_hash(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert pbkdf2_hasher.verify("test_password", "sha256$1000000$salt$'jeQtcwdQriGf31yAmWkfnBveO3bJFuVOeG7QN8IPlLk='")


def test_pbkdf2_hasher_verifies_incorrect_hash(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert (
        pbkdf2_hasher.verify("wrong_password", "sha256$1000000$salt$'jeQtcwdQriGf31yAmWkfnBveO3bJFuVOeG7QN8IPlLk='")
        is False
    )


def test_pbkdf2_hasher_returns_different_hashes_for_different_salts(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert pbkdf2_hasher.encode("test_password", "salt1") != pbkdf2_hasher.encode("test_password", "salt2")


def test_pbkdf2_hasher_returns_different_hashes_for_different_passwords(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert pbkdf2_hasher.encode("password1", "salt") != pbkdf2_hasher.encode("password2", "salt")


def test_pbkdf2_hasher_decodes_correct_hash(pbkdf2_hasher: PBKDF2PasswordHasher) -> None:
    assert pbkdf2_hasher.decode("sha256$1000000$salt$'jeQtcwdQriGf31yAmWkfnBveO3bJFuVOeG7QN8IPlLk='") == {
        "algorithm": "sha256",
        "hash": "'jeQtcwdQriGf31yAmWkfnBveO3bJFuVOeG7QN8IPlLk='",
        "iterations": 1000000,
        "salt": "salt",
    }
