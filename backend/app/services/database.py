import logging
from typing import Optional

import numpy as np
import pymongo
from bson import ObjectId, errors
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, WriteConcernError, ConnectionFailure

from app.models.person import Person  
from app.utils.constants import RoleType  

logger = logging.getLogger(__name__)

class Database():

    #Client attualmente connesso
    current_client = None 

    def __init__(self, url: str, name: str, collection: str):

        self.url = url
        self.name_db = name
        self.collection_name = collection
        self.get_connection(self.url)

    @property
    def is_connected(self):
        return self.current_client is not None

    @classmethod
    def get_connection(cls, url):
        if cls.current_client is None:
            try:
                cls.current_client = pymongo.MongoClient(url)
                logger.info("Connessione al database avvenuta con successo.")
            except pymongo.errors.ConnectionError as e:
                logger.critical(f"Errore di connessione al database: {e}")
                raise
        return cls.current_client
    
    @classmethod
    def close_connection(cls):
        if cls.current_client is not None:
            cls.current_client.close()
            cls.current_client = None
            logger.info("Connessione al database chiusa.")
    
    #Formattazione degli id di mongodb
    @staticmethod
    def convert_to_objectid(id_string: str) -> Optional[ObjectId]:
        try:
            return ObjectId(id_string)
        except (errors.InvalidId, TypeError):
            return None
    
    @staticmethod
    def _person_to_document(person: Person) -> dict:
        """Serializza un oggetto Person per Mongo, rimuovendo _id vuoti."""
        person_dict = person.model_dump(by_alias=True, exclude_none=True)
        if person_dict.get("_id") is None:
            person_dict.pop("_id", None)
        return person_dict

    @staticmethod
    def _person_from_doc(doc: Optional[dict]) -> Optional[Person]:
        """Ricostruisce un Person da un documento Mongo."""
        if doc is None:
            return None
        try:
            return Person.model_validate(doc)
        except Exception as exc:
            logger.error(f"Documento Person non valido: {exc}")
            return None
    
    def get_collection(self):
        client = self.get_connection(self.url)
        db = client[self.name_db] 
        return db[self.collection_name]
    
    def add_person(self, person: Person) -> Optional[Person]:
        collection = self.get_collection()
        person_dict = self._person_to_document(person)

        try:
            result = collection.insert_one(person_dict)
            
            person.id = str(result.inserted_id)
            
            logger.debug(f"Utente: {person.name} {person.surname} aggiunto al database con ID: {result.inserted_id}")
            return person

        # --- GESTIONE ERRORI CON ROLLBACK ---
        
        except DuplicateKeyError as e:
            logger.error(f"Impossibile inserire. Chiave duplicata rilevata: {e}")
            self._rollback_user_slot(person)
            return None

        except WriteConcernError as e:
            logger.critical(f"Errore di scrittura: {e}")
            self._rollback_user_slot(person)
            return None

        except ConnectionFailure as e:
            logger.critical(f"ERRORE DI CONNESSIONE: Il database non è raggiungibile: {e}")
            self._rollback_user_slot(person)
            return None

        except Exception as e:
            logger.error(f"Errore sconosciuto durante l'inserimento: {e}")
            self._rollback_user_slot(person)
            return None

    @staticmethod
    def _rollback_user_slot(person: Person):
        if person.role == RoleType.USER:
            logger.warning("Rollback: Resetto lo slot User a causa di un errore DB.")
            Person.reset_user_slot()
        
    
    def remove_person(self, person_id: str) -> bool:
        collection = self.get_collection()

        oid = self.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido: {person_id}")
            return False

        result = collection.delete_one({"_id": oid})

        if result.deleted_count > 0:
            logger.info(f"Persona con ID {person_id} rimossa correttamente.")
            return True
        else:
            logger.warning(f"Nessuna persona trovata con ID {person_id}.")
            return False
    
    def get_all_people(self) -> list[Person]:
        collection = self.get_collection()
        cursor = collection.find()
        people: list[Person] = []
        for doc in cursor:
            person = self._person_from_doc(doc)
            if person is not None:
                people.append(person)
        return people

    def get_person(self, person_id: str) -> Optional[Person]:
        collection = self.get_collection()
        oid = self.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido: {person_id}")
            return None
        doc = collection.find_one({"_id": oid})
        return self._person_from_doc(doc)
    
    def update_person(self, person_id: str, update_data: Person | dict) -> Optional[Person]:
        collection = self.get_collection()

        oid = self.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido per aggiornamento: {person_id}")
            return None
        
        if person_id != str(oid):
            logger.warning(f"ID non coerente per aggiornamento: {person_id} vs {str(oid)}")
            return None # Sanity check, WARNING: dovrebbe essere sempre coerente
        
        if isinstance(update_data, Person):
            payload = self._person_to_document(update_data)
        else:
            payload = dict(update_data)

        payload.pop("_id", None)
        payload.pop("id", None)

        if not payload:
            logger.warning("Nessun dato valido fornito per l'aggiornamento.")
            return None

        updated_doc = collection.find_one_and_update(
            {"_id": oid},
            {"$set": payload},
            return_document=ReturnDocument.AFTER
        )

        if updated_doc:
            person = self._person_from_doc(updated_doc)
            if person:
                logger.info(f"Aggiornata persona {person_id}.")
            return person

        logger.warning(f"Nessuna persona trovata con ID {person_id} per l'aggiornamento.")
        return None
    
    def update_people(self, people: list) -> int:
        success_count = 0
        for person in people:
            p = None
            
            if person.id is None:
                p = self.add_person(person)                  
            elif person.id is not None:
                p = self.update_person(person.id, person)
            else:
                logger.error(f"Impossibile aggiornare persona con dati: {person}")
            
            if p is not None:
                    success_count += 1

        logger.info(f"Aggiornamento bulk completato per {success_count} di {len(people)} persone.")
        return success_count
        

    def get_all_encodings(self):
        people = self.get_all_people()
        
        known_encodings = []
        known_names = []

        for person in people:
            full_name = f"{person.name} {person.surname}"
            
            face_encodings_dict = person.encoding or {}
            if not face_encodings_dict:
                logger.warning(f"{full_name} risulta vuoto")
                continue

            for hash_key, encoding_list in face_encodings_dict.items():
                try: 
                    known_encodings.append(np.array(encoding_list))
                    known_names.append(full_name)
                except Exception as e:
                    logger.error(f"Saltato encoding corrotto per {full_name} (Hash: {hash_key}). Causa: {e}")
                    continue

        return known_names, known_encodings
    
    def drop_database(self):

        client = self.get_connection(self.url)
        client.drop_database(self.name_db) 
        logger.info(f"Database '{self.name_db}' eliminato con successo.")
        self.close_connection()
        logger.info(f"Connessione con {self.url} terminata.")


"""
come usare database.py 
==============================

Setup iniziale
--------------
>>> db = Database(url=\"mongodb://localhost:27017\", name=\"ddfr\", collection=\"people\") OPPURE PER BUILD USARE CONFIG.PY

Creare e salvare una persona
----------------------------
>>> from datetime import date
>>> nuova = Person(name=\"Mario\", surname=\"Rossi\", birthday=date(1990, 1, 1))
>>> salvata = db.add_person(nuova)
>>> print(salvata.id)

Ottenere tutte le persone (list[Person])
----------------------------------------
>>> people = db.get_all_people()
>>> for person in people:
...     print(person.name, person.age)

Leggere una singola persona
---------------------------
>>> found = db.get_person(salvata.id)
>>> if found:
...     print(found.relationship)

Aggiornare i dati
-----------------
>>> updated = db.update_person(
...     salvata.id,
...     {\"relationship\": RelationshipType.FIGLIO}
... )
>>> if updated:
...     print(updated.relationship)

Rimuovere una persona
---------------------
>>> db.remove_person(salvata.id)

Ottenere gli encoding facciali
------------------------------
>>> names, encodings = db.get_all_encodings()
>>> print(len(encodings), \"encoding trovati\")
"""
