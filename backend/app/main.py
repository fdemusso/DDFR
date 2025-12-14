from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from config import database_settings as set, path_settings, api_settings
from services import database

# Configurazione logging asincrono per migliorare prestazioni
os.makedirs(path_settings.logfolder, exist_ok=True)
log_filename = os.path.join(path_settings.logfolder, "app.log")

root_logger = logging.getLogger()
if not root_logger.handlers:
    # Crea queue per logging asincrono
    log_queue = Queue(-1)  # Nessun limite di dimensione
    
    # Handler finali che scriveranno effettivamente i log
    file_handler = logging.FileHandler(log_filename)
    stream_handler = logging.StreamHandler()
    
    # Formattazione
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # QueueListener gestisce i log in background
    queue_listener = QueueListener(log_queue, file_handler, stream_handler, respect_handler_level=True)
    queue_listener.start()
    
    # Configura il root logger con QueueHandler
    queue_handler = QueueHandler(log_queue)
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

from routers import websocket  # noqa: E402
from routers import route      # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events.

    Context manager for FastAPI application startup and shutdown events.
    Currently performs no operations, but can be extended for initialization
    and cleanup tasks.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded to the application.

    """
    yield


app = FastAPI(
    title=api_settings.app_name,
    description=api_settings.description,
    version=api_settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket.router)
app.include_router(route.router)


@app.get("/")
def read_root():
    """Return root endpoint status message.

    Returns:
        dict: A dictionary containing a status message indicating the server is active.

    """
    return {"message": "Server Face Recognition attivo"}

if __name__ == "__main__":
    import uvicorn
    import sys
    from config import api_settings

    use_https = "https" in sys.argv

    if use_https:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=api_settings.keypath,
            ssl_certfile=api_settings.certpath,
            reload=False  # Disabilitato per ottimizzare prestazioni in produzione
        )
    else:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",  # Ascolta su tutte le interfacce per accettare connessioni dalla rete
            port=8000,
            reload=False  # Disabilitato per ottimizzare prestazioni in produzione
        )