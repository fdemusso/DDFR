import face_recognition
import logging
import os
from database import Database
from utils.img import ImgValidation
logger = logging.getLogger(__name__)

class FaceSystem():

    

    def __init__(self, db_instance: Database):
        self.known_face_names=[]
        self.known_face_encodings=[]
        self.client : Database = db_instance
        self.load_database()


    @property
    def is_connected(self):
        return self.client is not None and self.client.is_connected()
    
    @property
    def dataset_integrity(self):
        if not self.is_connected:
            logger.error("Check integrità fallito: Database non connesso o istanza mancante.")
            return False
        
        if len(self.known_face_encodings) == len(self.known_face_names):
            return True
        
        logger.critical(f"ERRORE INTEGRITÀ: {len(self.known_face_names)} nomi ma {len(self.known_face_encodings)} encodings!")
        return False
    
    @property
    def is_operational(self): 
        if self.dataset_integrity:

            if len(self.known_face_names) > 0:
                return True
            
            logger.warning(f"Sistema integro ma VUOTO. Nessun volto caricato dal DB {self.client.name_db}.")
            return False
        return False
    
    def load_database(self):
        
        try:
            self.known_face_names, self.known_face_encodings = self.client.get_all_encodings()

            if self.is_operational:
                logger.info(f"FaceSystem avviato correttamente")
            else:
                logger.warning("FaceSystem avviato ma NON operativo (vedi errori sopra).")
                
        except Exception as e:
            logger.error(f"Errore critico durante il caricamento dal DB: {e}")
            

    def recognize_from_img(self, path, person_data: dict, remove_img : bool = False):

        #TODO: validare person_data
        
        
        img  = ImgValidation(path, remove_img)

        if not self.is_operational:
            return False
        
        if (person_data.get("encoding", None) is not None):
            logger.warning("Passato encoding già calcolato")
            return False
        
        if img.is_valid:
            logger.warning(f"Passato percorso non valido per {person_data.get("name", "Unknow")}")
            return False

        target = face_recognition.load_image_file(img.path)
        face = {
            img.hash: face_recognition.face_encodings(target, num_jitters=100)[0]
        }
        logger.debug(f"{img.hash}: Image Loaded. 128-dimension Face Encoding Generated.\n")

        # Inserimento nel database
        # TODO: aggiungere HASH
        # TODO: aggiunge encoding



