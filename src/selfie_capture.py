import face_recognition
import recognition
import cv2 # pip install opencv-python

def main():

    webcam = cv2.VideoCapture(0)
    ret, unknown_frame = webcam.read()
    unknow_name=input("Inserisci il nome della persona sconosciuta: ")
    cv2.imshow("Captured", unknown_frame)         
    cv2.imwrite("Img/PNG/" + unknow_name + ".png", unknown_frame)
    cv2.imshow("Persona Sconosciuta", unknown_frame)
    recognition.FolderScan()