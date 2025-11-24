from dotenv import load_dotenv
import os
import pymongo
import people
import logging
import numpy as np
logger = logging.getLogger(__name__)


def get_collection():

    default_uri = "mongodb://localhost:27017/"
    default_db_name = "ddfr_db"
    default_collection_name = "people"

    uri = os.getenv("LOCAL_MONGODB_URI", default_uri)
    db_name = os.getenv("DATABASE_NAME", default_db_name)
    collection_name = os.getenv("PEOPLE_COLLECTION", default_collection_name)

    try:
        client = pymongo.MongoClient(uri)
        db = client[db_name]
        collection = db[collection_name]
        logger.debug(f"Connected to MongoDB collection: {collection.name} in database: {db_name}")
        return collection
    except pymongo.errors.ConnectionError as e:
        logger.critical(f"Error connecting to MongoDB: {e}")
        raise



def insert_person(encoding, collection, img_hash):
    person_data = {
        "name": people.get_name(),
        "surname": people.get_surname(),
        "age": people.get_age(),
        "relationship": people.get_relationship(),
        "encoding": encoding.tolist(),  # Converti l'array NumPy in lista per la memorizzazione
    }
    if img_hash is not None:
        data = {"img_hash": img_hash}
        person_data.update(data)
    
    collection.insert_one(person_data)

def fetch_all_encodings(collection):
    encodings = {}

    for document in collection.find():
        name = document.get("name", "Unknown")
        surname = document.get("surname", "Unknown")
        full_name = f"{name} {surname}"
        encoding_list = document.get("encoding", [])

        if encoding_list:
            # Converti la lista di codifiche in un array NumPy
            encodings[full_name] = np.array(encoding_list)
        else:
            logger.warning(f"Nessuna codifica trovata per {full_name} nel database.")
    logger.debug(f"Fetched encodings for {len(encodings)} people from the database.")
    return encodings

def fetch_all_img_hash(collection):
    img_hashes = []
    cursor = collection.find({}, {"img_hash": 1, "_id": 0})
    for document in cursor:
        if "img_hash" in document:
            img_hashes.append(document["img_hash"])
    logger.debug(f"Fetched img_hashes: {img_hashes}")
    return img_hashes

def clear_database():
    """Elimina il database specificato"""
    uri = os.getenv("LOCAL_MONGODB_URI", "mongodb://localhost:27017/")
    client = pymongo.MongoClient(uri)
    db = client[os.getenv("DATABAE_NAME", "ddfr_db")]

    client.drop_database(db)
    logger.info(f"Database '{db}' eliminato.")
    client.close()
