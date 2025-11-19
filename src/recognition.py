import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle

all_face_encodings = {}

def RecognitionFromFile(FilePath, name):
    File_target = face_recognition.load_image_file(FilePath)
    all_face_encodings[name] = face_recognition.face_encodings(File_target)[0]    
    print(f"{name}: Image Loaded. 128-dimension Face Encoding Generated. \n")


def main():

    Flavio_path = 'Img/HEIC/Flavio.HEIC'
    Francesca_path = 'Img/HEIC/Francesca.HEIC'

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

    RecognitionFromFile(Flavio_File, "Flavio")
    RecognitionFromFile(Francesca_File, "Francesca")

    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)

if __name__ == "__main__":
    main()