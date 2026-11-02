from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://app:app@localhost:5433/images"
    test_database_url: str = "postgresql+psycopg://app:app@localhost:5433/images_test"
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()