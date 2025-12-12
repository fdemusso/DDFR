from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import os
from contextlib import asynccontextmanager

from config import database_settings as set, path_settings, api_settings
from services import database

# Configurazione logging prima degli import dei router
os.makedirs(path_settings.logfolder, exist_ok=True)
log_filename = os.path.join(path_settings.logfolder, "app.log")

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

from routers import websocket  # noqa: E402
from routers import route      # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
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
            reload=True
        )
    else:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True
        )
