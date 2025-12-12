from pydantic_settings import BaseSettings
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class DatabaseSettings(BaseSettings):
    url: str = "mongodb://localhost:27017/"
    name: str = "ddfr_db"
    collection: str = "people"
    hash: str 
    
    class Config:
        env_prefix = "DB_"
        env_file = ENV_FILE_PATH
        env_file_encoding = 'utf-8'
        extra = "ignore"

class PathSettings(BaseSettings):
    logfolder: str = os.path.join(BASE_DIR, "logs") 
    imgsfolder: str = os.path.join(BASE_DIR, "img")
    
    class Config:
        env_prefix = "LOG_"
        env_file = ENV_FILE_PATH
        env_file_encoding = 'utf-8'
        extra = "ignore"

class APISettings(BaseSettings):
    app_name: str = "DDFR API"
    description: str = "API per il riconoscimento facciale e la gestione delle persone"
    app_version: str = "1.0.0"
    tollerance: float = 0.5
    debug: bool = False
    keypath: str = "/Users/flaviodemusso/Desktop/DDFR/key.pem"
    certpath: str = "/Users/flaviodemusso/Desktop/DDFR/cert.pem"

    class Config:
        env_file = ENV_FILE_PATH
        env_file_encoding = 'utf-8'
        extra = "ignore"

database_settings = DatabaseSettings()
path_settings = PathSettings()
api_settings = APISettings()