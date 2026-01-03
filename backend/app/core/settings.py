from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "dev"
    bot_token: str
    miniapp_url: str
    database_url: str

    webhook_secret: str
    public_base_url: str


settings = Settings()