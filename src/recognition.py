import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle

# Percorso del database dei volti
DATABASE_PATH = 'dataset_faces.dat'
HEIC_FOLDER = "Img/HEIC"
PNG_FOLDER = "Img/PNG"

def RecognitionFromFile(FilePath, name):

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


def FolderScan():

    #Cartelle del progetto

    if not os.path.exists(DATABASE_PATH):
    # creare il file vuoto (solo la prima volta)
        open(DATABASE_PATH, "wb").close()
        print("Il database è stato creato")

    # Conversione HEIC in PNG
    for filename in os.listdir(HEIC_FOLDER):

        heif.register_heif_opener()
        full_path = os.path.join(HEIC_FOLDER, filename)
        name, ext = os.path.splitext(filename)

        filepng = f"{PNG_FOLDER}/{name}.png"

        if not os.path.exists(filepng):
            try: 
                img = Image.open(full_path)
                img.save(filepng, 'PNG')
            except Exception as e:
                print(f"Errore durante la conversione: {e}")

    # Riconoscimento volti dalle immagini PNG
    for filename in os.listdir(PNG_FOLDER):
        full_path = os.path.join(PNG_FOLDER, filename)
        name, ext = os.path.splitext(filename)
        RecognitionFromFile(full_path, name)
