from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import logging
import base64
import json
import time

from config import database_settings as set, api_settings
from services import database
import services.recognition as fr


logger = logging.getLogger(__name__)

# Creiamo il Router
router = APIRouter()
TOLLERANCE = api_settings.tollerance
# --- CARICAMENTO MODELLI / DATABASE ---
try:
    DATASET = database.Database(
        url=set.url,
        name=set.name,
        collection=set.collection,
    )
    faces = fr.FaceSystem(DATASET)
    last_faces_reload = time.time()
    FACES_RELOAD_INTERVAL = 10
    logger.info(f"Caricati {len(faces.know_face_id)} volti noti dal database.")
except Exception as e:
    logger.critical(f"Errore durante l'inizializzazione del database/riconoscimento: {e}", exc_info=True)
    # Inizializziamo variabili di fallback per permettere l'avvio del server
    DATASET = None
    faces = None
    last_faces_reload = time.time()
    FACES_RELOAD_INTERVAL = 10

@router.websocket("/ws")  # Nota: non è più @app, ma @router
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info(f"Client WebSocket connesso da {websocket.client}")
    except Exception as e:
        logger.error(f"Errore durante l'accettazione della connessione WebSocket: {e}")
        raise

    try:
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            # 1. Ricezione dati
            data = await websocket.receive_text()

            # 2. Parsing Immagine (Base64 -> OpenCV)
            try:
                if ',' in data:
                    header, encoded = data.split(",", 1)
                else:
                    encoded = data
                
                image_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    logger.warning("Impossibile decodificare il frame ricevuto")
                    continue
            except Exception as e:
                logger.error(f"Errore durante il parsing dell'immagine: {e}")
                continue

            # 3. Ottimizzazione (Resize 1/4)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Conversione BGR -> RGB
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

            # 4. Rilevamento Facce
            face_locations , face_encodings = fr.frame_recognition(rgb_small_frame)
            
            if process_this_frame:
                face_id = []
                now = time.time()
                global faces, last_faces_reload
                
                # Verifica che il sistema di riconoscimento sia inizializzato
                if faces is None or DATASET is None:
                    logger.warning("Sistema di riconoscimento non inizializzato, saltando il riconoscimento")
                    face_id = [None] * len(face_encodings)
                else:
                    if now - last_faces_reload > FACES_RELOAD_INTERVAL:
                        try:
                            # Ricarico i volti dal DB ma solo ogni FACES_RELOAD_INTERVAL secondi
                            faces = fr.FaceSystem(DATASET)
                            last_faces_reload = now
                            logger.info(f"Dataset volti aggiornato, tot: {len(faces.know_face_id)}")
                        except Exception as e:
                            logger.error(f"Errore durante il ricaricamento dei volti: {e}")

                    for face_encoding in face_encodings:
                        try:
                            # Confronto con i volti noti
                            matches = fr.face_recognition.compare_faces(faces.known_face_encodings, face_encoding, TOLLERANCE)
                            id = None

                            # Uso il volto più simile
                            face_distances = fr.face_recognition.face_distance(faces.known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                id = faces.know_face_id[best_match_index]

                            face_id.append(id)
                        except Exception as e:
                            logger.error(f"Errore durante il riconoscimento facciale: {e}")
                            face_id.append(None)

            process_this_frame = not process_this_frame 

            face_names = []
            if faces is not None:
                for id in face_id:
                    found = False
                    for people in faces.know_people:
                        if people.id == id:
                            name = people.name
                            face_names.append(name)
                            found = True
                            break
                    if not found:
                        face_names.append("Unknown")
            else:
                face_names = ["Unknown"] * len(face_id)
                        
                    
            faces_data = []
            # Costruiamo un oggetto completo per ogni volto rilevato
            # (top, right, bottom, left) sono le coordinate restituite da face_recognition
            for (top, right, bottom, left), name, id in zip(face_locations, face_names, face_id):
                person_data = None

                if id is not None and faces is not None:
                    for people in faces.know_people:
                        if people.id == id:
                            person_data = people
                            break

                if person_data is not None:
                    # Persona riconosciuta
                    relationship = getattr(person_data.relationship, "value", person_data.relationship)
                    role = getattr(person_data.role, "value", person_data.role)

                    face_dict = {
                        "id": f"{top}_{left}",
                        "name": person_data.name,
                        "surname": person_data.surname,
                        "age": person_data.age,
                        "relationship": relationship,
                        "role": role,
                        "top": top * 4,
                        "right": right * 4,
                        "bottom": bottom * 4,
                        "left": left * 4,
                    }
                else:
                    # Volto sconosciuto
                    face_dict = {
                        "id": f"{top}_{left}",
                        "name": "Unknown",
                        "surname": None,
                        "age": 0,
                        "relationship": None,
                        "role": None,
                        "top": top * 4,
                        "right": right * 4,
                        "bottom": bottom * 4,
                        "left": left * 4,
                    }

                faces_data.append(face_dict)

            # 6. Risposta
            await websocket.send_text(json.dumps({"status": "ok", "faces": faces_data}))

    except WebSocketDisconnect:
        logger.info("Client WebSocket disconnesso")
    except Exception as e:
        logger.critical(f"Errore WebSocket: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass