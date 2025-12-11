from fastapi import APIRouter, HTTPException
import logging

# Import corretti usando il package "app"
from services.recognition import FaceSystem
from services.database import Database
from config import database_settings as set
from models.person import Person

logger = logging.getLogger(__name__)
router = APIRouter()
logger.debug("Router inizializzato correttamente.")

# INIZIALIZZAZIONE DEI SERVIZI
# Usiamo gli stessi nomi di campo definiti in app.config.DatabaseSettings
db = Database(
    url=set.url,
    name=set.name,
    collection=set.collection,
)
Faces = FaceSystem(db)

logger.info("Servizi di database e riconoscimento inizializzati.")
logger.debug(f"Database connesso: {db.is_connected}")
logger.debug(f"Sistema di riconoscimento operativo: {Faces.is_operational}")
logger.info(f"Numero di volti noti caricati: {len(Faces.know_face_id)}")





@router.get("/")
async def home():
    return {"message": "Hello World"}
