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
    """MongoDB database service for person data management.

    Manages connections to MongoDB, handles CRUD operations for Person objects,
    and maintains a cached reference to the user/patient (role=USER) person.

    Attributes:
        current_client (Optional[pymongo.MongoClient]): Class-level MongoDB client instance.
        url (str): MongoDB connection URL.
        name_db (str): Database name.
        collection_name (str): Collection name within the database.
        patient (Optional[Person]): Cached reference to the user/patient person.

    """

    current_client = None 

    def __init__(self, url: str, name: str, collection: str):
        """Initialize Database instance and establish connection.

        Args:
            url (str): MongoDB connection URL.
            name (str): Database name.
            collection (str): Collection name.

        Raises:
            ConnectionFailure: If connection to MongoDB fails.
            ValueError: If connection URL conflicts with existing connection.

        """
        self.url = url
        self.name_db = name
        self.collection_name = collection
        self.get_connection(self.url)
        self.patient: Optional[Person] = None
        self.patient = self.check_patient_existence()

    @property
    def is_connected(self) -> bool:
        """Check if database connection is active.

        Returns:
            bool: True if connection is active and responsive, False otherwise.

        """
        if self.current_client is None:
            return False
        try:
            self.current_client.admin.command('ping')
            return True      
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return False

    def check_patient_existence(self) -> Optional[Person] | None:
        """Check if a patient (role=USER) exists in the database.

        Returns cached patient if available, otherwise queries the database.

        Returns:
            Optional[Person]: Patient person if found, None otherwise.

        """
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
    def get_connection(cls, url: str) -> pymongo.MongoClient | None:
        """Get or create MongoDB client connection.

        Creates a new connection if none exists, or validates existing connection.
        Uses singleton pattern to share connection across instances.

        Args:
            url (str): MongoDB connection URL.

        Returns:
            pymongo.MongoClient | None: MongoDB client instance, or None if URL is invalid.

        Raises:
            ConnectionFailure: If connection fails.
            ConfigurationError: If connection configuration is invalid.
            ValueError: If URL conflicts with existing connection.

        """
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
        """Close MongoDB connection and reset client.

        Closes the shared MongoDB client connection and sets it to None.

        """
        if cls.current_client is not None:
            cls.current_client.close()
            cls.current_client = None
    
    @staticmethod
    def convert_to_objectid(id_string: str) -> Optional[ObjectId]:
        """Convert string ID to MongoDB ObjectId.

        Args:
            id_string (str): String representation of MongoDB ObjectId.

        Returns:
            Optional[ObjectId]: ObjectId if valid, None otherwise.

        """
        if id_string is None:
             return None
        try:
            return ObjectId(id_string)
        except (errors.InvalidId, TypeError):
            logger.error(f"ID non valido per ObjectId: {id_string}")
            return None
    
    @staticmethod
    def _person_to_document(person: Person) -> dict:
        """Convert Person object to MongoDB document format.

        Serializes Person to dictionary, handling dates, enums, and numpy arrays
        in encoding dictionaries for MongoDB storage.

        Args:
            person (Person): Person object to serialize.

        Returns:
            dict: Dictionary ready for MongoDB insertion/update.

        """
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
        """Convert MongoDB document to Person object.

        Args:
            doc (Optional[dict]): MongoDB document dictionary.

        Returns:
            Optional[Person]: Person object if valid, None otherwise.

        """
        if doc is None:
            return None
        try:
            return Person.model_validate(doc)
        except Exception as exc:
            logger.error(f"Documento Person non valido: {exc}")
            return None
    
    def get_collection(self) -> pymongo.collection.Collection | None:
        """Get MongoDB collection instance.

        Returns:
            pymongo.collection.Collection | None: MongoDB collection instance, or None if connection fails.

        """
        client = None
        try :
            client = self.get_connection(self.url)
        except Exception as e:
            logger.critical(f"Impossibile collegarsi al database per ottenere la collezione: {e}")
            return None
        
        if client is None:
            return None
        
        db = client[self.name_db] 
        return db[self.collection_name]
    
    def add_person(self, person: Person) -> Optional[Person] | None:
        """Add a new person to the database.

        Inserts person document into MongoDB. Ensures only one USER role person exists.
        Updates person.id with the inserted document ID.

        Args:
            person (Person): Person object to insert.

        Returns:
            Optional[Person]: Person object with assigned ID if successful, None otherwise.

        Raises:
            DuplicateKeyError: If duplicate key constraint violation occurs.
            WriteConcernError: If write operation fails.
            ConnectionFailure: If database connection is lost.

        """
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
        """Reset user slot if person role is USER.

        Args:
            person (Person): Person object to check for USER role.

        """
        if person.role == RoleType.USER:
            Person.reset_user_slot()      
    
    def remove_person(self, person_id: str) -> bool:
        """Remove a person from the database by ID.

        ⚠️ **Deprecated**: This method is not currently used in the application.
        Consider implementing proper deletion endpoints if needed.

        Args:
            person_id (str): Person's MongoDB ObjectId as string.

        Returns:
            bool: True if person was deleted, False otherwise.

        """
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
        """Retrieve all people from the database.

        Uses projection to load only necessary fields for performance optimization.

        Returns:
            list[Person]: List of all Person objects in the database.

        """
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
        """Retrieve a person by ID.

        ⚠️ **Deprecated**: This method is not currently used in the application.
        The application primarily works with `get_all_people()` to load all persons
        for face recognition. Consider implementing REST API endpoints if individual
        person retrieval is needed.

        Args:
            person_id (str): Person's MongoDB ObjectId as string.

        Returns:
            Optional[Person]: Person object if found, None otherwise.

        """
        collection = self.get_collection()
        oid = Database.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido per il recupero dei dati: {person_id}")
            return None
        doc = collection.find_one({"_id": oid})
        return self._person_from_doc(doc)
    
    def update_person(self, person_id: str, update_data: Person | dict) -> Optional[Person]:
        """Update a person's data in the database.

        ⚠️ **Deprecated**: This method is only used internally by `update_people()` which
        itself is not used. Consider implementing REST API endpoints for person updates
        if needed.

        Args:
            person_id (str): Person's MongoDB ObjectId as string.
            update_data (Person | dict): Person object or dictionary with update fields.

        Returns:
            Optional[Person]: Updated Person object if successful, None otherwise.

        """
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
        """Update multiple people in the database.

        ⚠️ **Deprecated**: This method is not currently used in the application.
        Person management is primarily done through `add_person()` during initial setup.
        Consider implementing batch update functionality via REST API if needed.

        Adds new people (id=None) or updates existing ones based on their ID.

        Args:
            people (list): List of Person objects to add or update.

        Returns:
            int: Number of successfully processed people.

        """
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
        
    def get_all_encodings(self) -> tuple[list[str], list[np.ndarray]]:
        """Extract all face encodings from all people in the database.

        ⚠️ **Deprecated**: This method was used with the old `face_recognition` library.
        The current implementation uses `FaceEngine` which directly processes Person objects
        with encodings stored in the `encoding` field. Use `get_all_people()` instead and
        access encodings directly from Person objects.

        Returns:
            tuple[list[str], list[np.ndarray]]: (known_ids, known_encodings) where known_ids is a list of person IDs
                and known_encodings is a list of numpy arrays representing face embeddings.

        """
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
        """Drop the entire database and close connection.

        ⚠️ **Deprecated**: This method is not currently used in the application.
        Reserved for testing and maintenance purposes. Use with extreme caution
        as it permanently deletes all data.

        Permanently deletes the database and all its collections.
        Resets patient cache and closes connection.

        """
        client = self.get_connection(self.url)
        client.drop_database(self.name_db) 
        if hasattr(self, "patient"):
            self.patient = None
        self.close_connection()
