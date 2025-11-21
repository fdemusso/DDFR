import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle
import logging

# Percorso del database dei volti
DATABASE_PATH = 'dataset_faces.dat'
IMG_FOLDER = "Img"
TEMP_FOLDER = "Temp"

def ConvertAnyToPng(FilePath, name, ext):
   
    filepng = f"{IMG_FOLDER}/{TEMP_FOLDER}/{name}.png"

    #Creo la cartella per le immagini temporanee se non esiste
    temp = f"{IMG_FOLDER}/{TEMP_FOLDER}"
    if not os.path.exists(temp):
        os.makedirs(temp)

    print(f"CONVERTANYTOPNG: Conversione file {FilePath} con ext = {ext} in PNG...")
    # Converto Heic in PNG
    if ext.lower() == ".heic":
        heif.register_heif_opener()

        if not os.path.exists(filepng):
            try: 
                img = Image.open(FilePath)
                img.save(filepng, 'PNG')
                return filepng
            except Exception as e:
                print(f"CONVERTANYTOPNG: Errore durante la conversione: {e}")
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
        print("CONVERTANYTOPNG: Formato non supportato per la conversione.")
        return None

def RecognitionFromFile(FilePath, name):

    # Verifico che il file esista
    if FilePath is None:
        return False
    
    # Leggo il database esistente o creo dict vuoto
    if os.path.exists(DATABASE_PATH) and os.path.getsize(DATABASE_PATH) > 0:
        with open(DATABASE_PATH, 'rb') as f:
            all_face_encodings = pickle.load(f)
    else:
        all_face_encodings = {}

    face_names = list(all_face_encodings.keys())

    # faccio l'encoding solo per i nomi che non sono presenti
    if name in face_names:
        print(f"Volto di {name} già presente")
    else:
        File_target = face_recognition.load_image_file(FilePath)
        all_face_encodings[name] = face_recognition.face_encodings(File_target, num_jitters=100)[0]
        print(f"{name}: Image Loaded. 128-dimension Face Encoding Generated.\n")

    # Risalvo tutto il dict
    with open(DATABASE_PATH, 'wb') as f:
        pickle.dump(all_face_encodings, f)

    return True

def FolderScan():

    #Cartelle del progetto
    if not os.path.exists(DATABASE_PATH):
    # creare il file vuoto (solo la prima volta)
        open(DATABASE_PATH, "wb").close()
        print("FOLDERSCAN: Il database è stato creato")

    for filename in os.listdir(IMG_FOLDER):
        # Prendo tutti gli elementi di IMG_FOLDER
        full_path = os.path.join(IMG_FOLDER, filename)
        name, ext = os.path.splitext(filename)
        print(f"FOLDERSCAN: Trovato file: {full_path},{filename} con estensione: {ext}")
        PngPath = ConvertAnyToPng(full_path, name, ext)

        # Filtro per quelli che è possibile convertire
        if PngPath is None:
            print(f"FOLDERSCAN: Impossibile convertire il file: {filename}")
            continue
        else:
            print(f"FOLDERSCAN: Scansione file: {PngPath}")
            if (RecognitionFromFile(PngPath, name)):
                continue
            else:
                print(f"FOLDERSCAN: Errore nella scansione del file: {filename}")

    temp = f"{IMG_FOLDER}/{TEMP_FOLDER}"
    if not os.path.exists(temp):
        os.remove(temp)

