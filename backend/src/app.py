# Main file per l'esecuzione del riconoscimento facciale
import face_recognition
import cv2
from flask import Flask, Response, render_template

# Moduli per la gestione delle variabili d'ambiente
from dotenv import load_dotenv
load_dotenv()

# Moduli di terze parti
import numpy as np
import pickle

# Moduli standard
import logging
import datetime
import os
import hashlib

# Moduli custom
import recognition
import database

# Directory per i file di log
logger = logging.getLogger(__name__)
app = Flask(__name__)

# Valori < 0.6 rendono il modello più preciso
TOLERANCE = 0.55
CLEAN_DATABASE = os.getenv("CLEAN_DATABASE", "False").lower() in ("true", "1", "t")

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

    else:  
        #Verde per i riconosciuti        
        block(0,255,0)

def webcamstream(collection):
    webcam = cv2.VideoCapture(0)
    logger.info('Webcam inizializzata.')
    clear_terminal()

    # avvia scansione volti
    if (recognition.FolderScan(collection)):
        logger.info("Scansione completa dispobibile nel main")
    else:
        logger.critical("Terminazione del programma a causa di un errore nella scansione delle immagini.")
        return

    # Carico i volti dal database

    all_face_encodings = database.fetch_all_encodings(collection)

    # Grab the list of names and the list of encodings
    
    known_face_names = list(all_face_encodings.keys())
    known_face_encodings = np.array(list(all_face_encodings.values()))
    logger.info('Caricamento dei volti completato.')

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
        #cv2.imshow("Video Feed", frame)

        # # Esco con 'q'
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     logger.info('Chiusura del programma di riconoscimento facciale.')
        #     break

        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            webcam.release()
            logger.info('Webcam rilasciata e tutte le finestre chiuse.')

@app.route('/video_feed')
def video_feed():

    # --- Inizio configurazione dei log ---
    if not os.path.exists(recognition.LOGS):
        os.makedirs(recognition.LOGS)

    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logging.basicConfig(filename=f"{recognition.LOGS}/{time}.log", level=logging.INFO)
    logger.info('Avviato il programma di riconoscimento facciale.')

    # --- Fine configurazione dei log ---

    # Loggo l'opzione di pulizia del database
    if CLEAN_DATABASE:
        logger.warning("Opzione di pulizia del database abilitata.")
        
        def database_outh():
            password_input = input("Inserisci la password per pulire il database: ").strip()
            hashed_input = hashlib.md5(password_input.encode()).hexdigest()
            stored_hash = os.getenv("DATABASE_PASSWORD", "")

            if hashed_input == stored_hash:
                return True
            else:
                return False
            
        # Autentico l'utente admin del database
        if database_outh():
            database.clear_database()
            logger.info("Database pulito all'avvio del programma.")
        else:
            print("Password errata. Terminazione del programma.")
            logger.critical("Password per la pulizia del database errata. Terminazione del programma.")
            return


    # Connessione al database MongoDB
    collection = database.get_collection()

    if collection is None:
        logger.critical("Connessione al database MongoDB non riuscita.")
        return
    webcamstream(collection)
    return Response(webcamstream(database.get_collection()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')

        # rilascio il controllo della webcam
        # webcam.release()
        # cv2.destroyAllWindows()
        # logger.info('Webcam rilasciata e tutte le finestre chiuse.')

