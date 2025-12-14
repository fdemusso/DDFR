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
    """Database connection configuration settings for MongoDB.

    Loads settings from .env file using the "DB_" prefix.
    All environment variables must be prefixed with DB_ to be recognized.

    Attributes:
        url (str): MongoDB connection URL. Default: "mongodb://localhost:27017/".
        name (str): Database name. Default: "ddfr_db".
        collection (str): MongoDB collection name. Default: "people".
        hash (str): Hash for data security. Required, no default value.

    """

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
    """File system path configuration settings.

    Loads settings from .env file using the "LOG_" prefix.
    All environment variables must be prefixed with LOG_ to be recognized.

    Attributes:
        logfolder (str): Directory path for log files. Default: "logs-{timestamp}" in backend directory.
        imgsfolder (str): Directory path for image storage. Default: "img" in app directory.

    """

    logfolder: str = os.path.join(BACKEND_DIR, f"logs-{_STARTUP_TIMESTAMP}")
    imgsfolder: str = os.path.join(BASE_DIR, "img")
    
    class Config:
        env_prefix = "LOG_"
        env_file = ENV_FILE_PATH
        env_file_encoding = 'utf-8'
        extra = "ignore"

class APISettings(BaseSettings):
    """API application configuration settings.

    Loads settings from .env file using the "APP_" prefix.
    All environment variables must be prefixed with APP_ to be recognized.

    Attributes:
        host (str): API server host address. Default: "192.168.1.69".
        port (int): API server port number. Default: 8000.
        app_name (str): Application name. Default: "DDFR API".
        description (str): API description. Default: "API per il riconoscimento facciale e la gestione delle persone".
        app_version (str): Application version. Default: "1.0.0".
        tollerance (float): Face recognition tolerance threshold. Default: 0.5.
        debug (bool): Enable debug mode. Default: False.
        use_https (bool): Enable HTTPS. Default: False.
        keypath (Optional[str]): Path to SSL private key file. Default: None.
        certpath (Optional[str]): Path to SSL certificate file. Default: None.

    """

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