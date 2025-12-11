from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

from config import database_settings as set, path_settings, api_settings
from services import database

# Configurazione del logging
# IMPORTANTE: il logging va configurato PRIMA di importare router o altri moduli
# che usano `logging.getLogger(__name__)` e scrivono log a livello modulo.
os.makedirs(path_settings.logfolder, exist_ok=True)

# Un solo file di log "fisso" per tutto il backend FastAPI
log_filename = os.path.join(path_settings.logfolder, "app.log")

# Evita di aggiungere più volte gli stessi handler (utile con reload/uvicorn)
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

# Solo dopo aver configurato il logging importiamo i router,
# così anche i log eseguiti in fase di import vengono registrati.
from routers import websocket  # noqa: E402
from routers import route      # noqa: E402


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


# Inclusione dei router
app.include_router(websocket.router)
app.include_router(route.router)  # API HTTP classiche


@app.get("/")
def read_root():
    return {"message": "Server Face Recognition attivo"}

if __name__ == "__main__":
    import uvicorn
    import sys
    from config import api_settings

    use_https = "https" in sys.argv

    if use_https:
        print("Modalità HTTPS attiva, assicurati di aver installato correttamente i certificati")

        # Configurazione e avvio del app

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port = 8000,
            ssl_keyfile= api_settings.keypath,
            ssl_certfile= api_settings.certpath,
            reload= True
        )
    else:
        print("Modalità HTTP attiva")
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port = 8000,
            reload= True
        )
