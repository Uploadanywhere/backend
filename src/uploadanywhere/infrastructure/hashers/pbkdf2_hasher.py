import base64
import hashlib
import secrets

from uploadanywhere.infrastructure.hashers.base_hasher import BasePasswordHasher


class PBKDF2PasswordHasher(BasePasswordHasher):
    _algorithm = "sha256"
    _iterations = 1_000_000

    def decode(self, encoded: str) -> dict[str, str | int | None]:
        algorithm, iterations, salt, _hash = encoded.split("$", 3)
        assert algorithm == self._algorithm
        return {
            "algorithm": algorithm,
            "hash": _hash,
            "iterations": int(iterations),
            "salt": salt,
        }

    def encode(self, password: str, salt: str | bytes | None = None) -> str:
        if not password:
            return ""
        if salt is None:
            salt = self.salt()

        salt = self._force_bytes(salt)

        encoded = hashlib.pbkdf2_hmac(str(self._algorithm), password.encode("utf-8"), salt, self._iterations)
        _hash = base64.b64encode(encoded).decode("ascii").strip()
        return f"{self._algorithm}${self._iterations:d}${salt.decode('utf-8')}${_hash!r}"

    def verify(self, password: str, encoded: str) -> bool:
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, str(decoded["salt"]))
        return secrets.compare_digest(self._force_bytes(encoded), self._force_bytes(encoded_2))
