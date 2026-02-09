from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # current environment
    ENVIRONMENT: str

    API_PREFIX: str = "/api/v1"
    API_VERSION: str = "v1.0"
    API_NAME: str = "Enrollment API"
    API_DESCRIPTION: str = "A simple API for a course enrollment platform"

    # DB
    API_DB: str
    API_DB_USER: str
    API_DB_PORT: str
    SYNC_DB_URL: str
    ASYNC_DB_URL: str
    API_DB_PASSWORD: str

    # Test DB
    ASYNC_TEST_DB_URL: str

    # Argon2
    ARGON2_PEPPER: str

    # JWT
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_TIME: int
    REFRESH_TOKEN_EXPIRE_TIME: int
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str

    # Sentry
    SENTRY_SDK_DSN: str

    # Admin User
    ADMIN_NAME: str
    ADMIN_EMAIL: str
    ADMIN_NATIONALITY: str
    ADMIN_PASSWORD: str

    # Task Broker
    BROKER_URL: str


settings = Settings()
