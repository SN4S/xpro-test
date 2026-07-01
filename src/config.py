from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "mysql+aiomysql://app_user:app_password@mysql:3306/test_db"
    ENVIRONMENT: str = "local"


settings = AppConfig()
