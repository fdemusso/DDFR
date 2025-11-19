import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle
import recognition

webcam = cv2.VideoCapture(0)
DATABASE_PATH = 'dataset_faces.dat'

# Valori < 0.6 rendono il modello più preciso
TOLERANCE = 0.5

# Funzione per pulire il terminale
def clear_terminal():
    if os.name == "nt":       # Windows
        os.system("cls")
    else:                     # macOS o Linux
        os.system("clear")


def writeretangle(frame, left, top, right, bottom, name):

    # Disegno l'effettivo rettangolo con il nome sotto
    def block(blu, green, red):
    
        cv2.rectangle(frame, (left, top), (right, bottom), (blu, green, red), 2)
        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (blu, green, red), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1) #white rgb

    # Colore del rettangolo in base al riconoscimento
    # TODO: riconoscere il volto del paziente
    if name == "Sconosciuto":
        #Rosso per gli sconosciuti
        block(0,0,255) 
        print("Volto Sconosciuto Rilevato! \n")
        scelta=input("Vuoi aggiungerlo al database si(s) o no(n)?")
        if scelta.lower() == 's':
            ret, unknown_frame = webcam.read()
            cv2.imwrite("Img/PNG/Captured.png", unknown_frame)
            with open(DATABASE_PATH, 'wb') as f:
                pickle.dump(unknown_frame, f)
            return
        elif scelta.lower() == 'n':
            return
        else:
            print("Volto non aggiunto.\n")



    else:  
        #Verde per i riconosciuti        
        block(0,255,0)


def main():
    # ---- Setto la videocamera di base ----

    
    clear_terminal()

    # avvia scansione volti
    recognition.FolderScan()

    # Carico i volti dal database
    with open(recognition.DATABASE_PATH, 'rb') as f:
        all_face_encodings = pickle.load(f)

    # Grab the list of names and the list of encodings
    known_face_names = list(all_face_encodings.keys())
    known_face_encodings = np.array(list(all_face_encodings.values()))


    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:

        ret, frame = webcam.read()

        #Riduco la risoluzione per velocizzare il processo
        small_frame = cv2.resize(frame, None, fx=0.20, fy=0.20)
        rgb_small_frame = cv2.cvtColor(small_frame, 4)

        #Riconosco i volti 
                
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # ottengo i nomi dei volti riconosciuti
        if process_this_frame:

            face_names = []

            for face_encoding in face_encodings:

                # Identifico gli sconosciuti
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding,TOLERANCE)
                name = "Sconosciuto"

                # Calcola con precisione il volto della persona
                # TODO: migliorare la soglia di riconoscimento
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        # Stabilisco quali frame processare e quali no
        process_this_frame = not process_this_frame 

        # Mostro i risultati
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 5
            right *= 5
            bottom *= 5
            left *= 5

            # Disegno il rettangolo attorno al volto
            writeretangle(frame, left, top, right, bottom, name)

        # Mostro il video
        cv2.imshow("Video Feed", frame)

        

        # Esco con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # rilascio il controllo della webcam
    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()