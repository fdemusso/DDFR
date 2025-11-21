import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle
import logging

# Percorso del database dei volti
LOGS = 'logs'
DATABASE_PATH = 'dataset_faces.dat'
IMG_FOLDER = "Img"
TEMP_FOLDER = "Temp"
logger = logging.getLogger(__name__)

def GetAllFaceEncodings():
    # Leggo il database esistente o creo dict vuoto
    if os.path.exists(DATABASE_PATH) and os.path.getsize(DATABASE_PATH) > 0:
        with open(DATABASE_PATH, 'rb') as f:
            all_face_encodings = pickle.load(f)
    else:
        all_face_encodings = {}
    return all_face_encodings

def IsNameInDatabase(name):

    all_face_encodings = GetAllFaceEncodings()

    face_names = list(all_face_encodings.keys())
    if name in face_names:
        logger.info(f"Volto di {name} già presente")
        return True
    else:
        return False

def ConvertAnyToPng(FilePath, name, ext):
   
    if IsNameInDatabase(name):
        logger.debug(f"Volto di {name} già presente, salto la conversione.")
        return None
    
    filepng = f"{IMG_FOLDER}/{TEMP_FOLDER}/{name}.png"

    if os.path.exists(filepng):
        logger.info(f"File PNG temporaneo già esistente: {filepng}")
        return filepng

    #Creo la cartella per le immagini temporanee se non esiste
    temp = f"{IMG_FOLDER}/{TEMP_FOLDER}"
    if not os.path.exists(temp):
        os.makedirs(temp)

    # Converto Heic in PNG
    if ext.lower() == ".heic":
        heif.register_heif_opener()

        if not os.path.exists(filepng):
            try: 
                img = Image.open(FilePath)
                img.save(filepng, 'PNG')
                return filepng
            except Exception as e:
                logger.error(f"Errore durante la conversione: {e}")
                return None

    # Converto Heic in PNG
    elif ext.lower() in [".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".png"]:
        img = Image.open(FilePath)
        img.save(filepng, 'PNG')
        return filepng

     # Se è già PNG lo ritorno così com'è
    elif ext.lower() == ".png":
        return FilePath
    else:
        logger.error("Formato non supportato per la conversione.")
        return None

def RecognitionFromFile(FilePath, name):

    # Verifico che il file esista
    if FilePath is None:
        return False
    if not IsNameInDatabase(name):

        all_face_encodings = GetAllFaceEncodings()
        File_target = face_recognition.load_image_file(FilePath)
        all_face_encodings[name] = face_recognition.face_encodings(File_target, num_jitters=100)[0]
        logger.debug(f"{name}: Image Loaded. 128-dimension Face Encoding Generated.\n")
    else:
        return True
    # Risalvo tutto il dict
    with open(DATABASE_PATH, 'wb') as f:
        pickle.dump(all_face_encodings, f)
        logger.info(f"Database aggiornato con il volto di: {name}")

    try:
        if os.path.exists(FilePath):
            os.remove(FilePath)
    except Exception as e:
        logger.error(f"Errore durante la rimozione del file temporaneo: {e}")

        

    return True

def FolderScan():

    #Cartelle del progetto
    if not os.path.exists(DATABASE_PATH):
    # creare il file vuoto (solo la prima volta)
        open(DATABASE_PATH, "wb").close()
        logger.info("Il database è stato creato")

    for filename in os.listdir(IMG_FOLDER):
        # Prendo tutti gli elementi di IMG_FOLDER
        full_path = os.path.join(IMG_FOLDER, filename)
        name, ext = os.path.splitext(filename)
        
        if IsNameInDatabase(name):
            continue

        logger.debug(f"Trovato file: {full_path},{filename} con estensione: {ext}")
        PngPath = ConvertAnyToPng(full_path, name, ext)

        # Filtro per quelli che è possibile convertire
        if PngPath is None:
            continue
        else:
            if (RecognitionFromFile(PngPath, name)):
                continue
            else:
                logger.error(f"Errore nella scansione del file: {filename}")

