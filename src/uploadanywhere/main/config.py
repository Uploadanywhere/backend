from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists


class PostgresConfig:
    dsn: str = env.str("POSTGRES_DSN", default="postgres://guest:guest@localhost:5432/guest?sslmode=disable")


class AuthConfig:
    session_ttl_in_days: int = env.int("SESSION_TTL_IN_DAYS", default=180)


class Config:
    auth: AuthConfig = AuthConfig()
    postgres: PostgresConfig = PostgresConfig()
