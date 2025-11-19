import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np

# ---- Setto la videocamera di base ----

webcam = cv2.VideoCapture(0)
# Percorso del file HEIC di input
Flavio_path = 'Flavio.HEIC'
Francesca_path = 'Francesca.HEIC'

# ---- converto l'immagine HEIC in png ----
# Registra l'opener HEIF
heif.register_heif_opener()
# Percorso del file PNG di output
Flavio_File = 'Flavio.png'
Francesca_File = 'Francesca.png'

try:
    # Apri l'immagine HEIC
    Flavio_img = Image.open(Flavio_path)
    Francesca_img = Image.open(Francesca_path)
    # Salva l'immagine in formato PNG
    Flavio_img.save(Flavio_File, 'PNG')
    Francesca_img.save(Francesca_File, 'PNG')
    print(f"File convertito con successo: {Flavio_File} e {Francesca_File}")
except Exception as e:
    print(f"Errore durante la conversione: {e}")


#Prova con due facce

#Target e encoding facce

#Flavio
Flavio_target = face_recognition.load_image_file(Flavio_File)
Flavio_encoding = face_recognition.face_encodings(Flavio_target)[0]

print("Flavio: Image Loaded. 128-dimension Face Encoding Generated. \n")

#Francesca
Francesca_target = face_recognition.load_image_file(Francesca_File)
Francesca_encoding = face_recognition.face_encodings(Francesca_target)[0]
print("Francesca: Image Loaded. 128-dimension Face Encoding Generated. \n")

known_face_encodings = [
    Flavio_encoding,
    Francesca_encoding
]
known_face_names = [
    "Flavio",
    "Francesca"
]



# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    ret, frame = webcam.read()

    small_frame = cv2.resize(frame, None, fx=0.20, fy=0.20)
    rgb_small_frame = cv2.cvtColor(small_frame, 4)

    #Riconosco i volti 
            
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    if process_this_frame:
        

        face_locations = face_recognition.face_locations(rgb_small_frame)
        frame_encodings = face_recognition.face_encodings(rgb_small_frame)

        face_names = []



        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Sconosciuto"

            # Calcola con precisione il volto della persona
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 5
        right *= 5
        bottom *= 5
        left *= 5

        if name == "Sconosciuto":

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        else:          
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
        


    cv2.imshow("Video Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        #Rimuovo l'immagine convertita in png
        try:
            os.remove(Flavio_File)
            print(f"File '{Flavio_File}' deleted successfully.")
            os.remove(Francesca_File)
            print(f"File '{Francesca_File}' deleted successfully.")
        except FileNotFoundError:
            print(f"File '{Flavio_File}' or {Francesca_File} not found.")
        break


webcam.release()
cv2.destroyAllWindows()

