import pymongo
import logging
import numpy as np
from bson import ObjectId, errors 
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
    
    @staticmethod
    def convert_to_objectid(id_string: str):
        try:
            return ObjectId(id_string)
        except (errors.InvalidId, TypeError):
            return None
    
    @staticmethod
    def normalize_doc(doc: dict) -> dict:
        if doc is None:
            return None
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return doc
    
    def get_collection(self):
        client = self.get_connection(self.url)
        db = client[self.name_db] 
        return db[self.collection_name]
    
    def add_person(self, person_data: dict):
        collection = self.get_collection()
        result = collection.insert_one(person_data)
        name = person_data.get("name", "Unknown")
        surname = person_data.get("surname", "Unknown")
        logger.debug(f"Utente:{name} {surname} aggiunto al database con ID: {result.inserted_id}")
        return str(result.inserted_id)
    
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
    
    def get_all_people(self):
        collection = self.get_collection()
        cursor = collection.find()
        return [self.normalize_doc(doc) for doc in cursor]

    def get_person(self, person_id):
        collection = self.get_collection()
        oid = self.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido: {person_id}")
            return None
        doc = collection.find_one({"_id": oid})
        return self.normalize_doc(doc)
    
    def update_person(self, person_id: str, update_data: dict) -> bool:
        collection = self.get_collection()

        oid = self.convert_to_objectid(person_id)
        if oid is None:
            logger.warning(f"ID non valido per aggiornamento: {person_id}")
            return False
        
        update_data.pop("_id", None)
        update_data.pop("id", None)

        if not update_data:
            return False

        # 3. Eseguo l'update con $set
        result = collection.update_one(
            {"_id": oid},            
            {"$set": update_data}    
        )

        if result.matched_count > 0:
            logger.info(f"Aggiornata persona {person_id}. Campi modificati: {result.modified_count}")
            return True
        else:
            logger.warning(f"Nessuna persona trovata con ID {person_id} per l'aggiornamento.")
            return False
        

    def get_all_encodings(self):
        people = self.get_all_people()
        
        known_encodings = []
        known_names = []

        for person in people:
            name = person.get("name", "Unknown")
            surname = person.get("surname", "Unknown")
            full_name = f"{name} {surname}"
            
            encoding_list = person.get("encoding", [])

            if encoding_list:
                known_names.append(full_name)
                known_encodings.append(np.array(encoding_list))
            else:
                logger.warning(f"Nessuna codifica per {full_name}")

        return known_names, known_encodings
    
    def drop_database(self):

        client = self.get_connection(self.url)
        client.drop_database(self.name_db) 
        logger.info(f"Database '{self.name_db}' eliminato con successo.")
        self.close_connection()
        logger.info(f"Connessione con {self.url} terminata.")
