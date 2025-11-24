from pydantic import BaseSettings
import os

class DatabaseSettings(BaseSettings):
    url: str = "mongodb://localhost:27017/"
    name: str = "ddfr_db"
    collection: str = "people"
    hash: str 
    
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

class LoggingSettings(BaseSettings):
    logfolder: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

    class Config:
        env_prefix = "LOG_"
        env_file = ".env"

class APISettings(BaseSettings):
    app_name: str = "DDFR API"
    description: str = "API per il riconoscimento facciale e la gestione delle persone"
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"

# Istanze globali da importare
database_settings = DatabaseSettings()
logging_settings = LoggingSettings()
api_settings = APISettings()
