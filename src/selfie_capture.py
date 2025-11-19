import face_recognition
import cv2 # pip install opencv-python

def selfie_capture():

    webcam = cv2.VideoCapture(0)
    
    # print("Persona Sconosciuta Rilevata! Cattura un selfie.")

    ret, frame = webcam.read()
    rgb_small_frame = cv2.cvtColor(small_frame, 4)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    small_frame = cv2.resize(frame, None, fx=0.20, fy=0.20)

    label = "Sconosciuto"
    ret, unknown_frame = webcam.read()
    unknow_name=input("Inserisci il nome della persona sconosciuta: ")
    cv2.imshow("Captured", unknown_frame)         
    cv2.imwrite(unknow_name + ".jpg", unknown_frame)
    process_this_frame = not process_this_frame

    if face_locations:
        top, right, bottom, left = face_locations[0]

        top *= 5
        right *= 5
        bottom *= 5
        left *= 5

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 0, 255), cv2.FILLED)
        label_font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, label, (left + 6, bottom - 6), label_font, 0.8, (255, 255, 255), 1)

        cv2.imshow("Persona Sconosciuta", unknown_frame)
