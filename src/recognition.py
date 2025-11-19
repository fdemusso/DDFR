import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle



def RecognitionFromFile(FilePath, name):
    db_path = 'dataset_faces.dat'

    # Leggo il database esistente o creo dict vuoto
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        with open(db_path, 'rb') as f:
            all_face_encodings = pickle.load(f)
    else:
        all_face_encodings = {}

    face_names = list(all_face_encodings.keys())

    # faccio l'encoding solo per i nomi che non sono presenti
    if name in face_names:
        print(f"Volto di {name} già presente")
    else:
        File_target = face_recognition.load_image_file(FilePath)
        all_face_encodings[name] = face_recognition.face_encodings(File_target)[0]
        print(f"{name}: Image Loaded. 128-dimension Face Encoding Generated.\n")

    # Risalvo tutto il dict
    with open(db_path, 'wb') as f:
        pickle.dump(all_face_encodings, f)


def FolderScan():

    #Cartelle del progetto
    heicfolder = "Img/HEIC"
    pngfolder = "Img/PNG"

    if not os.path.exists("dataset_faces.dat"):
    # creare il file vuoto (solo la prima volta)
        open("dataset_faces.dat", "wb").close()
        print("Il database è stato creato")

    for filename in os.listdir(heicfolder):

        heif.register_heif_opener()
        full_path = os.path.join(heicfolder, filename)
        name, ext = os.path.splitext(filename)

        filepng = f"{pngfolder}/{name}.png"

        if not os.path.exists(filepng):
            try: 
                img = Image.open(full_path)
                img.save(filepng, 'PNG')
            except Exception as e:
                print(f"Errore durante la conversione: {e}")


    for filename in os.listdir(pngfolder):
        full_path = os.path.join(pngfolder, filename)
        name, ext = os.path.splitext(filename)
        RecognitionFromFile(full_path, name)

