from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # DB
    API_DB: str
    API_DB_USER: str
    API_DB_PORT: str
    SYNC_DB_URL: str
    ASYNC_DB_URL: str
    API_DB_PASSWORD: str


settings = Settings()
