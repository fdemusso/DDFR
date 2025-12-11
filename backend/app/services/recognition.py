import face_recognition
import logging
import os
from services.database import Database
from utils.img import ImgValidation
from models.person import Person
logger = logging.getLogger(__name__)

class FaceSystem():


    def __init__(self, db_instance: Database):
        self.know_face_id=[]
        self.known_face_encodings=[]
        self.know_people = []
        self.client : Database = db_instance
        self.load_database()


    @property
    def is_connected(self):
        return self.client is not None and self.client.is_connected
    
    @property
    def dataset_integrity(self):
        if not self.is_connected:
            logger.error("Check integrità fallito: Database non connesso o istanza mancante.")
            return False
        
        if len(self.known_face_encodings) == len(self.know_face_id):
            return True
        
        logger.critical(f"ERRORE INTEGRITÀ: {len(self.know_face_id)} nomi ma {len(self.known_face_encodings)} encodings!")
        return False
    
    @property
    def is_operational(self): 
        if self.dataset_integrity:

            if len(self.know_face_id) > 0:
                return True
            
            logger.warning(f"Sistema integro ma VUOTO. Nessun volto caricato dal DB {self.client.name_db}.")
            return False
        return False
    
    
    def load_database(self):
        
        try:
            self.know_face_id, self.known_face_encodings = self.client.get_all_encodings()
            self.know_people = self.client.get_all_people()

            if self.is_operational:
                logger.info(f"FaceSystem avviato correttamente")
            elif not self.is_operational:
                logger.warning("FaceSystem avviato ma NON operativo (vedi errori sopra).")
                
        except Exception as e:
            logger.error(f"Errore critico durante il caricamento dal DB: {e}")
            

    # Person dovrebbe essere passato per rifermimento
    # Person rappresenta una singola persona
    def recognize_from_img(self, paths : list, person_data: Person, remove_img : bool = False):


        if not self.is_operational:
            return False
        
        face = {} # Questo diventerà il dizionario {hash: encoding_list}
        volti_trovati = 0
        immagini_processate = 0
        
        logger.info(f"Inizio elaborazione di {len(paths)} immagini per {person_data.name if person_data.name else 'Unknown'}")
        
        for path in paths:
            img = ImgValidation(path, remove_img)
            
            if not img.is_valid:
                nome_persona = person_data.name if person_data.name else "Unknown"
                logger.warning(f"Passato percorso non valido per {nome_persona}: {path}")
                continue

            try:
                immagini_processate += 1
                target = face_recognition.load_image_file(img.path)
                
                # Generiamo gli encoding
                found_encodings = face_recognition.face_encodings(target, num_jitters=100)

                if len(found_encodings) > 0:
                    # Prendiamo il primo volto trovato (indice 0)
                    
                    face[img.hash] = found_encodings[0].tolist()
                    volti_trovati += 1
                    
                    logger.info(f"Volto trovato e encoding generato: {img.hash} (da {os.path.basename(path)})")
                else:
                    logger.warning(f"Nessun volto trovato nell'immagine: {os.path.basename(path)}")

            except Exception as e:
                logger.error(f"Errore elaborazione immagine {path}: {e}")
                continue
        
        logger.info(f"Elaborazione completata: {immagini_processate} immagini processate, {volti_trovati} volti trovati")
            
        if not face:
            logger.error("Nessun encoding valido generato dai percorsi forniti.")
            return False

        # Unisce i nuovi encoding con quelli esistenti (se presenti)
        encoding_precedenti = len(person_data.encoding) if person_data.encoding else 0
        if person_data.encoding is not None:
            # Conta quanti sono nuovi vs sostituiti
            nuovi_hash = set(face.keys())
            hash_esistenti = set(person_data.encoding.keys())
            hash_nuovi = nuovi_hash - hash_esistenti
            hash_sostituiti = nuovi_hash & hash_esistenti
            
            person_data.encoding.update(face)
            totale_finale = len(person_data.encoding)
            
            if hash_sostituiti:
                logger.info(f"Uniti {len(face)} encoding: {len(hash_nuovi)} nuovi, {len(hash_sostituiti)} sostituiti. Da {encoding_precedenti} a {totale_finale} encoding totali")
            else:
                logger.info(f"Aggiunti {len(face)} nuovi encoding. Da {encoding_precedenti} a {totale_finale} encoding totali")
        else:
            person_data.encoding = face
            logger.info(f"Aggiunti {len(face)} nuovi encoding (nessun encoding precedente)")

        # Inserimento nel DB
        try:
            if person_data.id is  None:     
                inserted_id = self.client.add_person(person_data)
                if inserted_id is None:
                    logger.warning("Impossibile aggiungere la persona (add_person ha restituito None)")
                    return False
                logger.info(f"Persona aggiunta al database con ID: {inserted_id.id}")
            else: 
                logger.info(f"Aggiornamento persona con ID: {person_data.id}")
                updated_person = self.client.update_person(str(person_data.id), person_data)
                if updated_person is None:
                    logger.warning("Impossibile aggiornare la persona (update_person ha restituito None)")
                    return False
                logger.info(f"Persona aggiornata con successo. Totale encoding: {len(updated_person.encoding) if updated_person.encoding else 0}")
                            
        except Exception as e:
                logger.error(f"Errore durante salvataggio DB: {e}")
                return False
        
        # Ricarica il database per verificare che i volti siano stati salvati
        self.load_database()
        logger.info(f"Database ricaricato. Sistema operativo: {self.is_operational}")
        
        return True


def frame_recognition(rgb_small_frame):
    face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=1)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    return face_locations, face_encodings