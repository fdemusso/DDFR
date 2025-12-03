import os
import logging
from datetime import datetime
from typing import List, Dict

import face_recognition

import app.services.database as database
from app.config import database_settings as set, path_settings
from app.models.person import Person
from app.utils.constants import RoleType

# --- CONFIGURAZIONE AMBIENTE ---
# Creo (se non esiste) la cartella dei log definita in config.py
os.makedirs(path_settings.logfolder, exist_ok=True)
log_filename = os.path.join(
    path_settings.logfolder, f"local-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def _build_demo_person() -> Person:
    """Crea l'istanza demo da inserire nel DB."""
    return Person(
        name="Antonello",
        surname="Giannuzzi",
        birthday=datetime(2005, 9, 24),
        role=RoleType.GUEST,
    )


def _encode_faces(paths: List[str]) -> Dict[str, list[float]]:
    """
    Replica in modo semplificato la logica di FaceSystem.recognize_from_img
    per generare gli encoding a partire da una o più immagini locali.
    """
    faces: Dict[str, list[float]] = {}

    for path in paths:
        if not os.path.exists(path):
            logger.warning(f"Percorso immagine non trovato: {path}")
            continue
        try:
            target = face_recognition.load_image_file(path)
            found_encodings = face_recognition.face_encodings(target, num_jitters=100)

            if len(found_encodings) > 0:
                key = os.path.basename(path)
                faces[key] = found_encodings[0].tolist()
                logger.info(f"Encoding generato per immagine {path}")
            else:
                logger.warning(f"Nessun volto trovato nell'immagine: {path}")

        except Exception as e:  # pragma: no cover - script utilitario
            logger.error(f"Errore elaborazione immagine {path}: {e}")
            continue

    return faces


def main() -> None:
    # Connessione al DB
    dataset = database.Database(
        url=set.url,
        name=set.name,
        collection=set.collection,
    )

    demo_person = _build_demo_person()

    paths = ["/Users/flaviodemusso/Desktop/DDFR/backend/public/Img/IMG_5786.png"]

    encodings = _encode_faces(paths)
    if not encodings:
        logger.error("Nessun encoding valido generato. Interruzione script.")
        print("Inserimento fallito (nessun volto riconosciuto).")
        return

    demo_person.encoding = encodings

    saved = dataset.add_person(demo_person)

    if saved is not None:
        logger.info(f"Inserimento completato. ID: {saved.id}")
        print("Inserimento completato.")
    else:
        logger.error("Inserimento fallito da parte del Database.")
        print("Inserimento fallito.")


if __name__ == "__main__":
    main()