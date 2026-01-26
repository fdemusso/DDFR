from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging
import os
import tempfile
from typing import List
from datetime import datetime
from pathlib import Path

from services.recognition import FaceEngine
from services.database import Database
from config import database_settings as set, path_settings
from models.person import Person
from utils.constants import RelationshipType, RoleType

logger = logging.getLogger(__name__)
router = APIRouter()

# Inizializza database e engine (singleton pattern)
_dataset = None
_engine = None

def get_database() -> Database:
    """Get or create database instance."""
    global _dataset
    if _dataset is None:
        _dataset = Database(
            url=set.url,
            name=set.name,
            collection=set.collection,
        )
    return _dataset

def get_engine() -> FaceEngine:
    """Get or create face engine instance."""
    global _engine, _dataset
    if _engine is None:
        if _dataset is None:
            _dataset = get_database()
        people = _dataset.get_all_people()
        _engine = FaceEngine(people)
    return _engine

@router.get("/")
async def home() -> dict:
    """Return home endpoint greeting message.

    Returns:
        dict: A dictionary containing a greeting message.

    """
    return {"message": "Hello World"}

@router.get("/api/status")
async def get_status() -> dict:
    """Check database status and patient existence.

    Returns:
        dict: Dictionary with has_patient (bool) and total_people (int).

    """
    logger.info("=== INIZIO CHECK STATUS DATABASE ===")
    try:
        logger.info("1. Ottenimento istanza database...")
        dataset = get_database()
        logger.info(f"   Database ottenuto: url={set.url}, name={set.name}, collection={set.collection}")
        
        # Forza refresh della cache del paziente per assicurarsi di avere dati aggiornati
        logger.info("2. Reset cache paziente...")
        old_patient = dataset.patient
        if old_patient:
            logger.info(f"   Paziente in cache prima del reset: ID={old_patient.id}, name={old_patient.name}")
        else:
            logger.info(f"   Paziente in cache prima del reset: None")
        dataset.patient = None
        
        logger.info("3. Controllo esistenza paziente nel database...")
        patient = dataset.check_patient_existence()
        if patient:
            logger.info(f"   Risultato check_patient_existence: Person(id={patient.id}, name={patient.name}, surname={patient.surname}, role={patient.role})")
        else:
            logger.info(f"   Risultato check_patient_existence: None")
        
        if patient is None:
            logger.warning("   WARNING: NESSUN PAZIENTE TROVATO!")
        else:
            logger.info(f"   OK: Paziente trovato: ID={patient.id}, name={patient.name}, surname={patient.surname}, role={patient.role}")
            if dataset.patient:
                logger.info(f"   Paziente in cache dopo check: ID={dataset.patient.id}, name={dataset.patient.name}")
        
        logger.info("4. Recupero tutte le persone dal database...")
        all_people = dataset.get_all_people()
        logger.info(f"   Totale persone trovate: {len(all_people)}")
        
        # Log dettagliato di tutte le persone (senza encoding)
        for idx, person in enumerate(all_people):
            has_encoding = person.encoding is not None and len(person.encoding) > 0
            encoding_count = len(person.encoding) if person.encoding else 0
            logger.info(f"   Persona {idx+1}: ID={person.id}, name={person.name}, surname={person.surname}, role={person.role}, encoding_count={encoding_count}")
        
        # Verifica manuale se c'è un USER nel database
        logger.info("5. Verifica manuale presenza USER nel database...")
        collection = dataset.get_collection()
        if collection is None:
            logger.error("   ERRORE: Collection e None!")
        else:
            logger.info(f"   Collection ottenuta: {collection.name}")
            manual_query = {"role": RoleType.USER.value}
            logger.info(f"   Query manuale: {manual_query}")
            manual_doc = collection.find_one(manual_query, {"encoding": 0})  # Escludi encoding dalla projection
            if manual_doc:
                logger.info(f"   Documento trovato con query manuale: _id={manual_doc.get('_id')}, role={manual_doc.get('role')}, name={manual_doc.get('name')}, surname={manual_doc.get('surname')}")
            else:
                logger.info(f"   Nessun documento trovato con query manuale")
        
        has_patient = patient is not None
        logger.info(f"6. Risultato finale: has_patient={has_patient}, total_people={len(all_people)}")
        logger.info("=== FINE CHECK STATUS DATABASE ===")
        
        return {
            "has_patient": has_patient,
            "total_people": len(all_people)
        }
    except Exception as e:
        logger.error(f"ERRORE nel controllo stato database: {e}", exc_info=True)
        logger.error(f"   Tipo errore: {type(e).__name__}")
        logger.error(f"   Messaggio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nel controllo stato: {str(e)}")

@router.post("/api/person")
async def create_person(
    name: str = Form(...),
    surname: str = Form(...),
    birthday: str = Form(...),
    relationship: str = Form(...),
    role: str = Form(...),
    photos: List[UploadFile] = File(...)
) -> dict:
    """Create a new person with multiple photos.

    Processes uploaded photos to extract face encodings, combines them,
    and saves the person to the database.

    Args:
        name: Person's first name.
        surname: Person's last name.
        birthday: Birthday in ISO format (YYYY-MM-DD).
        relationship: Relationship type (from RelationshipType enum).
        role: Role type (from RoleType enum).
        photos: List of uploaded image files.

    Returns:
        dict: Created person data with ID.

    Raises:
        HTTPException: If validation fails, no faces detected, or database error.

    """
    try:
        # Validazione role
        try:
            role_enum = RoleType(role.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Role non valido. Valori accettati: {[r.value for r in RoleType]}"
            )
        
        # Validazione relationship
        try:
            relationship_enum = RelationshipType(relationship.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Relationship non valido. Valori accettati: {[r.value for r in RelationshipType]}"
            )
        
        # Validazione birthday
        try:
            birthday_date = datetime.fromisoformat(birthday)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato birthday non valido. Usa formato ISO (YYYY-MM-DD)"
            )
        
        # Validazione nome e cognome
        if len(name) < 2 or len(name) > 50:
            raise HTTPException(status_code=400, detail="Nome deve essere tra 2 e 50 caratteri")
        if len(surname) < 2 or len(surname) > 50:
            raise HTTPException(status_code=400, detail="Cognome deve essere tra 2 e 50 caratteri")
        
        # Validazione foto
        if not photos or len(photos) == 0:
            raise HTTPException(status_code=400, detail="Almeno una foto è richiesta")
        
        # Assicura che la cartella img esista
        os.makedirs(path_settings.imgsfolder, exist_ok=True)
        
        # Processa le foto
        dataset = get_database()
        engine = get_engine()
        all_encodings = {}
        temp_files = []
        
        try:
            for photo in photos:
                # Salva file temporaneo
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=os.path.splitext(photo.filename)[1] if photo.filename else ".jpg",
                    dir=path_settings.imgsfolder
                )
                temp_files.append(temp_file.name)
                
                # Scrivi contenuto del file
                content = await photo.read()
                temp_file.write(content)
                temp_file.close()
                
                # Processa immagine
                logger.info(f"Processando foto: {photo.filename}")
                new_data = engine.analyze_img(temp_file.name)
                
                if new_data is not None:
                    all_encodings.update(new_data)
                    logger.info(f"Volto trovato in {photo.filename}")
                else:
                    logger.warning(f"Nessun volto trovato in {photo.filename}")
            
            # Verifica che almeno un encoding sia stato trovato
            if not all_encodings:
                raise HTTPException(
                    status_code=400,
                    detail="Nessun volto valido trovato nelle foto caricate"
                )
            
            # Crea Person object
            person = Person(
                name=name,
                surname=surname,
                birthday=birthday_date,
                relationship=relationship_enum,
                role=role_enum,
                encoding=all_encodings
            )
            
            # Salva nel database
            saved_person = dataset.add_person(person)
            
            if saved_person is None:
                raise HTTPException(
                    status_code=500,
                    detail="Errore durante il salvataggio nel database"
                )
            
            # Ricarica engine con nuove persone
            global _engine
            _engine = None
            engine = get_engine()
            
            # Prepara risposta
            response_data = {
                "id": str(saved_person.id),
                "name": saved_person.name,
                "surname": saved_person.surname,
                "birthday": saved_person.birthday.isoformat(),
                "relationship": saved_person.relationship.value,
                "role": saved_person.role.value,
                "photos_processed": len(all_encodings)
            }
            
            return response_data
            
        finally:
            # Pulisci file temporanei
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Errore nella rimozione file temporaneo {temp_file}: {e}")
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore durante la creazione della persona: {e}")
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")
