from fastapi import APIRouter, HTTPException
import logging

# Import corretti usando il package "app"
from app.services.recognition import FaceSystem
from app.services.database import Database
from app.config import database_settings as set
from app.models.person import Person

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


# ESEMPIO DI UTILIZZO DEI SERVIZI
# people = db.get_all_people()
# logger.info(f"Numero di persone nel database: {len(people)}")
# se si lavora localmente si può aggiornare people nel database cosi:
#db.update_people(people) così si aggiornano i record con i nuovi encoding di tutte le persone
# bisogna mantenere la coerenza tra databse e dati locali
# quindi people = db.get_all_people() --> aggiornare i dati locali --> db.update_people(people)





@router.get("/")
async def home():
    return {"message": "Hello World"}
