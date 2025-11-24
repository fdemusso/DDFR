from fastapi import FastAPI
from app.api.routes import router
from app.config import logging_settings, api_settings

import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Configurazione del logging
os.makedirs(logging_settings.log_folder, exist_ok=True)
log_filename = os.path.join(logging_settings.log_folder, f"app-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

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

# Inclusione dei router
app.include_router(router)
