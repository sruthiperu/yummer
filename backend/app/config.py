from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # set default vals
    database_url: str
    # add AI API key
    google_client_id: str = ""      
    google_client_secret: str = ""  
    jwt_secret: str = ""            

    # look in .env
    class Config:
        env_file = ".env"

settings = Settings() 
