import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os
import numpy as np
import pickle
import recognition


def writeretangle(frame, left, top, right, bottom, name):

    def block(blu, green, red):
    
        cv2.rectangle(frame, (left, top), (right, bottom), (blu, green, red), 2)
        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (blu, green, red), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1) #white rgb

    if name == "Sconosciuto":
        #Rosso per gli sconosciuti
        block(0,0,255) 

    else:  
        #Verde per i riconosciuti        
        block(0,255,0)


def main():
    # ---- Setto la videocamera di base ----

    webcam = cv2.VideoCapture(0)

    # avvia scansione volti
    recognition.FolderScan()

    # Load face encodings
    with open('dataset_faces.dat', 'rb') as f:
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

        small_frame = cv2.resize(frame, None, fx=0.20, fy=0.20)
        rgb_small_frame = cv2.cvtColor(small_frame, 4)

        #Riconosco i volti 
                
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        if process_this_frame:

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

            writeretangle(frame, left, top, right, bottom, name)

        cv2.imshow("Video Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()