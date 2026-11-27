import hashlib
import secrets

from uploadanywhere.infrastructure.hashers.base_hasher import BasePasswordHasher


class MD5PasswordHasher(BasePasswordHasher):
    _algorithm = "md5"

    def decode(self, encoded: str) -> dict[str, str | int | None]:
        algorithm, salt, hashed = encoded.split("$", 2)
        assert algorithm == self._algorithm
        return {
            "algorithm": algorithm,
            "hash": hashed,
            "salt": salt,
        }

    def encode(self, password: str, salt: str | bytes | None = None) -> str:
        if not password:
            return ""
        if salt is None:
            salt = self.salt()

        salt = self._force_bytes(salt)

        encoded = hashlib.md5(salt + password.encode("utf-8")).hexdigest()  # ruff: ignore[hashlib-insecure-hash-function]
        return f"{self._algorithm}${salt.decode('utf-8')}${encoded}"

    def verify(self, password: str, encoded: str) -> bool:
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, str(decoded["salt"]))
        return secrets.compare_digest(self._force_bytes(encoded), self._force_bytes(encoded_2))
