import face_recognition
import cv2
from PIL import Image
import pillow_heif as heif
import os

webcam = cv2.VideoCapture(0)
# Percorso del file HEIC di input
input_path = input("Target Image File > ")
# converto l'immagine HEIC in png

# Registra l'opener HEIF
heif.register_heif_opener()
# Percorso del file PNG di output
image_file = 'prova.png'

try:
    # Apri l'immagine HEIC
    img = Image.open(input_path)
    # Salva l'immagine in formato PNG
    img.save(image_file, 'PNG')
    print(f"File convertito con successo: {image_file}")
except Exception as e:
    print(f"Errore durante la conversione: {e}")


#
target_image = face_recognition.load_image_file(image_file)
target_encoding = face_recognition.face_encodings(target_image)[0]

print("Image Loaded. 128-dimension Face Encoding Generated. \n")

target_name = input("Target Name > ")


process_this_frame = True

while True:
    ret, frame = webcam.read()

    small_frame = cv2.resize(frame, None, fx=0.20, fy=0.20)
    rgb_small_frame = cv2.cvtColor(small_frame, 4)

    if process_this_frame:

        face_locations = face_recognition.face_locations(rgb_small_frame)
        frame_encodings = face_recognition.face_encodings(rgb_small_frame)

        if frame_encodings:
            frame_face_encoding = frame_encodings[0]
            match = face_recognition.compare_faces([target_encoding], frame_face_encoding)[0]
            label = target_name if match else "Unknown"

    process_this_frame = not process_this_frame

    if face_locations:
        top, right, bottom, left = face_locations[0]

        top *= 5
        right *= 5
        bottom *= 5
        left *= 5

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 255, 0), cv2.FILLED)
        label_font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, label, (left + 6, bottom - 6), label_font, 0.8, (255, 255, 255), 1)

    cv2.imshow("Video Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #Rimuovo l'immagine convertita in png
        try:
            os.remove(image_file)
            print(f"File '{image_file}' deleted successfully.")
        except FileNotFoundError:
            print(f"File '{image_file}' not found.")
        break


webcam.release()
cv2.destroyAllWindows()

