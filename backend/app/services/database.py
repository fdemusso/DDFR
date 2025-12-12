import logging
from typing import Optional

import numpy as np
import pymongo
from bson import ObjectId, errors
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, WriteConcernError, ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime, date
from models.person import Person  
from pymongo.uri_parser import parse_uri
from utils.constants import RoleType  

logger = logging.getLogger(__name__)

class Database():
    current_client = None 

    def __init__(self, url: str, name: str, collection: str):

        self.url = url
        self.name_db = name
        self.collection_name = collection
        self.get_connection(self.url)
        self.patient: Optional[Person] = None
        self.patient = self.check_patient_existence()

    @property
    def is_connected(self):
        if self.current_client is None:
            return False
        try:
            self.current_client.admin.command('ping')
            return True      
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return False

    def check_patient_existence(self) -> Optional[Person] | None:
        cached_patient: Optional[Person] = getattr(self, "patient", None)
        if cached_patient is not None:
            return cached_patient
        
        collection = self.get_collection()
        query = {"role": RoleType.USER.value}
        doc = collection.find_one(query)
        patient = self._person_from_doc(doc)
        if patient:
            self.patient = patient
        return patient

    @classmethod
    def get_connection(cls, url):
        if url is None:
            logger.error("URL di connessione non fornito.")
            return None
        
        if cls.current_client is None:
            try:
                cls.current_client = pymongo.MongoClient(url)
                cls.current_client.admin.command('ping')
            except (pymongo.errors.ConnectionFailure, pymongo.errors.ConfigurationError) as e:
                logger.critical(f"Errore critico di connessione al database: {e}")
                cls.current_client = None
                raise
        else:
            try:
                parsed_uri = parse_uri(url)
                new_nodes = set(parsed_uri['nodelist'])
                current_node = cls.current_client.address 
                
                if current_node and current_node not in new_nodes:
                    error_msg = (
                        f"Connessione già esistente con un host diverso.\n"
                        f"Attivo: {current_node}\n"
                        f"Richiesto: {new_nodes} (da {url})"
                    )
                    logger.warning(error_msg)
                    raise ValueError(error_msg)
            except Exception as e:
                logger.error(f"Errore durante la verifica dell'URL esistente: {e}")

        return cls.current_client
    


    @classmethod
    def close_connection(cls):
        if cls.current_client is not None:
            cls.current_client.close()
            cls.current_client = None
    
    @staticmethod
    def convert_to_objectid(id_string: str) -> Optional[ObjectId]:
        if id_string is None:
             return None
        try:
            return ObjectId(id_string)
        except (errors.InvalidId, TypeError):
            logger.error(f"ID non valido per ObjectId: {id_string}")
            return None
    
    @staticmethod
    def _person_to_document(person: Person) -> dict:
        # Serializza Person per Mongo, gestendo date ed Enums
        person_dict = person.model_dump(by_alias=True, exclude_none=True)
        
        if person_dict.get("_id") is None:
            person_dict.pop("_id", None)

        if "birthday" in person_dict:
            b_day = person_dict["birthday"]
            if type(b_day) == date:
                person_dict["birthday"] = datetime(b_day.year, b_day.month, b_day.day)

        if "encoding" in person_dict and person_dict["encoding"] is not None:
            encoding_dict = person_dict["encoding"]
            if isinstance(encoding_dict, dict):
                serialized_encoding = {}
                for hash_key, encoding_value in encoding_dict.items():
                    if isinstance(encoding_value, np.ndarray):
                        serialized_encoding[hash_key] = encoding_value.tolist()
                    elif isinstance(encoding_value, list):
                        serialized_encoding[hash_key] = [float(x) for x in encoding_value]
                    else:
                        serialized_encoding[hash_key] = encoding_value
                person_dict["encoding"] = serialized_encoding

        for key, value in person_dict.items():
            if hasattr(value, "value"):  
                person_dict[key] = value.value

        return person_dict

    @staticmethod
    def _person_from_doc(doc: Optional[dict]) -> Optional[Person]:
        if doc is None:
            return None
        try:
            return Person.model_validate(doc)
        except Exception as exc:
            logger.error(f"Documento Person non valido: {exc}")
            return None
    
    def get_collection(self):
        client = None
        try :
            client = self.get_connection(self.url)
        except Exception as e:
            logger.critical(f"Impossibile collegarsi al database per ottenere la collezione: {e}")
            return None
        
        db = client[self.name_db] 
        return db[self.collection_name]
    
    def add_person(self, person: Person) -> Optional[Person] | None:
        collection = self.get_collection()
        person_dict = self._person_to_document(person)

        if person.role == RoleType.USER:
            if getattr(self, "patient", None) is not None:
                logger.error("Impossibile inserire. Esiste già un paziente registrato.")
                return None
        try:
            result = collection.insert_one(person_dict)
            person.id = str(result.inserted_id)
            if person.role == RoleType.USER:
                self.patient = person  
            return person
        
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
            Person.reset_user_slot()
        
    
    def remove_person(self, person_id: str) -> bool:
        collection = self.get_collection()

        oid = Database.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido per la rimozione: {person_id}")
            return False

        result = collection.delete_one({"_id": oid})

        if result.deleted_count > 0:
            cached_patient: Optional[Person] = getattr(self, "patient", None)
            if cached_patient is not None and str(cached_patient.id) == person_id:
                self.patient = None
            return True
        else:
            logger.warning(f"Nessuna persona trovata con ID {person_id}.")
            return False
    
    def get_all_people(self) -> list[Person]:
        collection = self.get_collection()
        # Projection: carica solo i campi necessari per ottimizzare prestazioni
        projection = {
            "_id": 1,
            "name": 1,
            "surname": 1,
            "encoding": 1,
            "role": 1,
            "relationship": 1,
            "birthday": 1
        }
        cursor = collection.find({}, projection)
        people: list[Person] = []
        for doc in cursor:
            person = self._person_from_doc(doc)
            if person is not None:
                people.append(person)
        return people

    def get_person(self, person_id: str) -> Optional[Person]:
        collection = self.get_collection()
        oid = Database.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido per il recupero dei dati: {person_id}")
            return None
        doc = collection.find_one({"_id": oid})
        return self._person_from_doc(doc)
    
    def update_person(self, person_id: str, update_data: Person | dict) -> Optional[Person]:
        collection = self.get_collection()

        oid = Database.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido per aggiornamento: {person_id}")
            return None
            
        
        if person_id != str(oid):
            logger.warning(f"ID non coerente per aggiornamento: {person_id} vs {str(oid)}")
            return None
        
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

        return success_count
        

    def get_all_encodings(self):
        people = self.get_all_people()
        
        known_encodings = []
        known_ids = []

        for person in people:
            id = person.id
            
            face_encodings_dict = person.encoding or {}
            if not face_encodings_dict:
                logger.warning(f"{id} risulta vuoto")
                continue

            for hash_key, encoding_list in face_encodings_dict.items():
                try: 
                    known_encodings.append(np.array(encoding_list))
                    known_ids.append(id)
                except Exception as e:
                    logger.error(f"Saltato encoding corrotto per {str(id)} (Hash: {hash_key}). Causa: {e}")
                    continue

        return known_ids, known_encodings
    
    def drop_database(self):
        client = self.get_connection(self.url)
        client.drop_database(self.name_db) 
        if hasattr(self, "patient"):
            self.patient = None
        self.close_connection()
