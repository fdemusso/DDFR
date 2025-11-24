import face_recognition
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle
import logging
import database
import hashlib

# Percorso del database dei volti
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.normpath(os.path.join(BASE_DIR, "..", "logs"))
IMG_FOLDER = os.path.normpath(os.path.join(BASE_DIR, "..", "Img"))
logger = logging.getLogger(__name__)

def hash_img(img):
    img_hash = hashlib.md5(Image.open(img).tobytes())
    return img_hash.hexdigest()

def compare_img(local_hash, collection):

    remote_hash = database.fetch_all_img_hash(collection)

    for rh in remote_hash:
        if local_hash == rh:
            return True
    
    return False

def ConvertAnyToPng(FilePath, name, ext):

    filepng = f"{IMG_FOLDER}/{name}.png"
    if ext.lower() == ".png" and filepng == FilePath:
        return FilePath
    
    # Converto Heic in PNG
    if ext.lower() == ".heic":
        heif.register_heif_opener()

        if not os.path.exists(filepng):
            try: 
                img = Image.open(FilePath)
                img.save(filepng, 'PNG')
                
            except Exception as e:
                logger.error(f"Errore durante la conversione: {e}")
                return None
            
            # Rimuovo il file originale dopo la conversione
            try:
                if os.path.exists(FilePath):
                    os.remove(FilePath)
            except Exception as e:
                logger.error(f"Errore durante la rimozione del file originale: {e}")
        
        return filepng

    # Converto Heic in PNG
    elif ext.lower() in [".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".png"]:
        img = Image.open(FilePath)
        img.save(filepng, 'PNG')
        # Rimuovo il file originale dopo la conversione
        try:
            if os.path.exists(FilePath):
                    os.remove(FilePath)
        except Exception as e:
            logger.error(f"Errore durante la rimozione del file originale: {e}")

        return filepng
    else:
        logger.error("Formato non supportato per la conversione.")
        return None

def RecognitionFromFile(collection, FilePath):

        # Verifico la connessione al database MongoDB
    if collection is None:
        logger.error("Impossibile connettersi al database MongoDB per il riconoscimento dei volti.")
        return False

    # Verifico che il file esista
    if os.path.exists(FilePath) is False:
        logger.error(f"File non trovato: {FilePath}")
        return False
    
    print(f"Elaborazione del file: {FilePath}")
    
    hash_value = hash_img(FilePath)
    if compare_img(hash_value, collection):
        print("Immagine già presente nel database")
        logger.info(f"{FilePath} già presente nel database")
        return True
    
    # Scansiono il primo volto trovato nell'immagine
    File_target = face_recognition.load_image_file(FilePath)
    face = {
        hash_value: face_recognition.face_encodings(File_target, num_jitters=100)[0]
    }
    logger.debug(f"{hash_value}: Image Loaded. 128-dimension Face Encoding Generated.\n")

    database.insert_person(face[hash_value], collection, hash_value)

    return True

def FolderScan(collection):

    # Verifico la connessione al database MongoDB
    if collection is None:
        logger.critical("Connessione al database MongoDB non riuscita.")
        return False
    else:
        logger.info("Connessione al database MongoDB riuscita.")

    imgs = os.listdir(IMG_FOLDER)
    if not imgs:
        logger.warning(f"Nessun file trovato nella cartella {IMG_FOLDER}.")
        return False
    
    for img in imgs:

        # Prendo tutti gli elementi di IMG_FOLDER
        path = os.path.join(IMG_FOLDER, img)
        name, ext = os.path.splitext(img)

        # Converto il file nel formato corretto
        PngPath = ConvertAnyToPng(path, name, ext)
        
        # Filtro per quelli che è possibile convertire
        if PngPath is not None:
            hash_value = hash_img(PngPath)
            if compare_img(hash_value, collection):
                continue
            else:
                response = input(f"Vuoi aggiungere il volto in {path} al database? (s/n): ").strip().lower()
                if response != 's':
                    logger.info(f"Aggiunta del volto in {path} saltata dall'utente.")
                    continue

                elif (RecognitionFromFile(collection, PngPath) and response == 's'):
                    continue
                else:
                    logger.error(f"Errore nella scansione del file: {img}")
       
    return True
