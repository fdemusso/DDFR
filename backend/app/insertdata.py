import os
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from services.recognition import FaceEngine

import services.database as database
from config import database_settings as set, path_settings
from models.person import Person
from utils.constants import RoleType

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
    return Person(
        name="Flavio",
        surname="De Musso",
        birthday=datetime(2005, 6, 17),
        role=RoleType.GUEST,
    )




def main() -> None:

    DATASET = database.Database(
        url=set.url,
        name=set.name,
        collection=set.collection,
    )
    people = DATASET.get_all_people() 
    engine = FaceEngine(people)   
    demo_person = _build_demo_person()
    
    all_encodings = {} 
    folder = Path(path_settings.imgsfolder)
    
    for elemento in folder.iterdir():
        if elemento.is_file() and not elemento.name.startswith('.'):
            print(f"Analisi di: {elemento.name}...")
            new_data = engine.analyze_img(elemento)

            if new_data is not None:
                all_encodings.update(new_data) 
                print(f" -> OK, volto trovato.")
            else:
                print(f" -> Nessun volto trovato o file non valido.")

    if not all_encodings:
        logger.error("Nessun encoding valido generato da nessuna foto.")
        return

    demo_person.encoding = all_encodings
    saved = DATASET.add_person(demo_person)

    if saved is not None:
        logger.info(f"Inserimento completato. ID: {saved.id} - Totale foto: {len(all_encodings)}")
        print("Inserimento completato.")
    else:
        logger.error("Inserimento fallito da parte del Database.")
        print("Inserimento fallito.")

if __name__ == "__main__":
    main()