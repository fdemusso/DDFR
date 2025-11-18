import face_recognition
import cv2

def main():
    #Definisco la telecamera di base per il proggetto
    webcam = cv2.VideoCapture(0)

    #Ottengo un immagine di prova
    image_file = input("prova.HEIC")
    
    #Traccio l'encoding dell'immagine
    target_image = face_recognition.load_image_file(image_file)
    target_encoding = face_recognition.face_encodings(target_image)[0]


if __name__ == "__main__":
    main()