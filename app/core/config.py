from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Network Route API"
    database_url: str = "sqlite:///./network_route.db"
    debug: bool = False
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
