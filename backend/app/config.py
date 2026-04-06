from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # set default vals
    database_url = str
    # add AI API key
    jwt: str = ""

    # look in .env
    class Config:
        file_env = ".env"

settings = Settings() 
