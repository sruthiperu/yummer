from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # set default vals
    database_url: str
    openai_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    jwt_secret: str = ""

    # local defaults
    frontend_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000/api/v1"
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    cookie_secure: bool | None = None

    # look in .env
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
