from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import websocket
from app.routers import route
from app.config import database_settings as set, path_settings, api_settings
from app.services import database

import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Configurazione del logging
os.makedirs(path_settings.logfolder, exist_ok=True)
log_filename = os.path.join(path_settings.logfolder, f"app-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Lifespan: gestisce startup e shutdown dell’app in un solo contesto
@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Startup: connessioni al database, risorse esterne, task periodici
    logger.info("Applicazione: startup iniziata")
    # yield indica che l’app ora comincia a servire le richieste
    yield
    # TODO: Shutdown: chiusura connessioni, pulizia risorse
    logger.info("Applicazione: shutdown in corso")


# Creazione dell'istanza FastAPI con il lifespan
app = FastAPI(
    title=api_settings.app_name,
    description=api_settings.description,
    version=api_settings.app_version,
    lifespan=lifespan,
)


# Configurazione CORS per poter comunicare con frontend su domini diversi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permette tutte le origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATASET = database.Database(
    url=set.url,
    name=set.name,
    collection=set.collection,
)


# Inclusione dei router
app.include_router(websocket.router)
app.include_router(route.router)  # API HTTP classiche


@app.get("/")
def read_root():
    return {"message": "Server Face Recognition attivo"}