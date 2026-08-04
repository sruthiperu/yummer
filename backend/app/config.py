from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # set default vals
    database_url: str
    openai_api_key: str = ""
    google_client_id: str = ""      
    google_client_secret: str = ""  
    jwt_secret: str = ""            

    # look in .env
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 
