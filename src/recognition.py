import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle

Flavio_path = 'Img/HEIC/Flavio.HEIC'
Francesca_path = 'Img/HEIC/Francesca.HEIC'

# ---- converto l'immagine HEIC in png ----
# Registra l'opener HEIF


heif.register_heif_opener()
# Percorso del file PNG di output
Flavio_File = 'Img/PNG/Flavio.png'
Francesca_File = 'Img/PNG/Francesca.png'

if not os.path.exists(Flavio_File):
    try: 
        Flavio_img = Image.open(Flavio_path)
        Flavio_img.save(Flavio_File, 'PNG')
    except Exception as e:
        print(f"Errore durante la conversione: {e}")  

if not os.path.exists(Francesca_File):
    try: 
        Francesca_img = Image.open(Francesca_path)
        Francesca_img.save(Francesca_File, 'PNG')
    except Exception as e:
        print(f"Errore durante la conversione: {e}") 

#Prova con due facce

#Target e encoding facce

all_face_encodings = {}

#Flavio
Flavio_target = face_recognition.load_image_file(Flavio_File)
all_face_encodings["Flavio"] = face_recognition.face_encodings(Flavio_target)[0]

print("Flavio: Image Loaded. 128-dimension Face Encoding Generated. \n")

#Francesca
Francesca_target = face_recognition.load_image_file(Francesca_File)
all_face_encodings["Francesca"] = face_recognition.face_encodings(Francesca_target)[0]
print("Francesca: Image Loaded. 128-dimension Face Encoding Generated. \n")

with open('dataset_faces.dat', 'wb') as f:
    pickle.dump(all_face_encodings, f)

