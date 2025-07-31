import math
import secrets

from uploadanywhere.application.interfaces.password_hasher import PasswordHasher

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_random_string(length: int, allowed_chars: str = RANDOM_STRING_CHARS) -> str:
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return "".join(secrets.choice(allowed_chars) for _ in range(length))


class BasePasswordHasher(PasswordHasher):
    """
    Abstract base class for password hashers

    When creating your own hasher, you need to override algorithm,
    verify(), encode() and safe_summary().

    PasswordHasher objects are immutable.
    """

    _algorithm: str | None = None
    _salt_entropy = 128

    def _force_bytes(self, string: str | bytes) -> bytes:
        if isinstance(string, bytes):
            return string
        return str(string).encode("utf-8")

    def _check_encode_args(self, password: str | None, salt: str | None) -> None:
        if password is None:
            raise TypeError("password must be provided.")
        if not salt or "$" in salt:
            raise ValueError("salt must be provided and cannot contain $.")

    def salt(self) -> str:
        """
        Generate a cryptographically secure nonce salt in ASCII with an entropy
        of at least `salt_entropy` bits.
        """
        # Each character in the salt provides
        # log_2(len(alphabet)) bits of entropy.
        char_count = math.ceil(self._salt_entropy / math.log2(len(RANDOM_STRING_CHARS)))
        return get_random_string(char_count, allowed_chars=RANDOM_STRING_CHARS)

    def verify(self, password: str, encoded: str) -> bool:
        """Check if the given password is correct."""
        raise NotImplementedError("subclasses of BasePasswordHasher must provide a verify() method")

    def encode(self, password: str, salt: str | bytes | None = None) -> str:
        """
        Create an encoded database value.

        The result is normally formatted as "algorithm$salt$hash" and
        must be fewer than 128 characters.
        """
        raise NotImplementedError("subclasses of BasePasswordHasher must provide an encode() method")

    def decode(self, encoded: str) -> dict[str, str | int | None]:
        """
        Return a decoded database value.

        The result is a dictionary and should contain `algorithm`, `hash`, and
        `salt`. Extra keys can be algorithm specific like `iterations` or
        `work_factor`.
        """
        raise NotImplementedError("subclasses of BasePasswordHasher must provide a decode() method.")
