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

    #Cartelle del progetto
    heicfolder = "Img/HEIC"
    pngfolder = "Img/PNG"


    for filename in os.listdir(heicfolder):

        heif.register_heif_opener()
        full_path = os.path.join(heicfolder, filename)
        name, ext = os.path.splitext(filename)
        
        print(name)
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

    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)

if __name__ == "__main__":
    main()