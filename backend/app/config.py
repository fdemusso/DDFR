from pydantic_settings import BaseSettings
import os
from datetime import datetime
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Vai alla directory backend (un livello sopra app/)
BACKEND_DIR = os.path.dirname(BASE_DIR)
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

# Genera timestamp unico all'avvio dell'applicazione
_STARTUP_TIMESTAMP = datetime.now().strftime('%Y%m%d-%H%M%S')

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
    logfolder: str = os.path.join(BACKEND_DIR, f"logs-{_STARTUP_TIMESTAMP}")
    imgsfolder: str = os.path.join(BASE_DIR, "img")
    
    class Config:
        env_prefix = "LOG_"
        env_file = ENV_FILE_PATH
        env_file_encoding = 'utf-8'
        extra = "ignore"

class APISettings(BaseSettings):
    host: str = "192.168.1.69"
    port: int = 8000
    app_name: str = "DDFR API"
    description: str = "API per il riconoscimento facciale e la gestione delle persone"
    app_version: str = "1.0.0"
    tollerance: float = 0.5
    debug: bool = False
    use_https: bool = False
    keypath: Optional[str] = None
    certpath: Optional[str] = None

    class Config:
        env_prefix = "APP_"
        env_file = ENV_FILE_PATH
        env_file_encoding = 'utf-8'
        extra = "ignore"

database_settings = DatabaseSettings()
path_settings = PathSettings()
api_settings = APISettings()