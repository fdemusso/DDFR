from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import logging
import base64
import json
import time

from app.config import database_settings as set
from app.services import database
import app.services.recognition as fr


logger = logging.getLogger(__name__)

# Creiamo il Router
router = APIRouter()

# --- CARICAMENTO MODELLI / DATABASE ---
DATASET = database.Database(
    url=set.url,
    name=set.name,
    collection=set.collection,
)
faces = fr.FaceSystem(DATASET)
last_faces_reload = time.time()
FACES_RELOAD_INTERVAL = 10
logger.info(f"Caricati {len(faces.know_face_id)} volti noti dal database.")

@router.websocket("/ws")  # Nota: non è più @app, ma @router
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client WebSocket connesso")

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
            if ',' in data:
                header, encoded = data.split(",", 1)
            else:
                encoded = data
            
            image_bytes = base64.b64decode(encoded)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
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
                if now - last_faces_reload > FACES_RELOAD_INTERVAL:
                    # Ricarico i volti dal DB ma solo ogni FACES_RELOAD_INTERVAL secondi
                    faces = fr.FaceSystem(DATASET)
                    last_faces_reload = now
                    logger.info(f"Dataset volti aggiornato, tot: {len(faces.know_face_id)}")

                for face_encoding in face_encodings:
                    # Confronto con i volti noti
                    matches = fr.face_recognition.compare_faces(faces.known_face_encodings, face_encoding, tolerance=0.6)
                    id = None

                    # Uso il volto più simile
                    face_distances = fr.face_recognition.face_distance(faces.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        id = faces.know_face_id[best_match_index]

                    face_id.append(id)

            process_this_frame = not process_this_frame 

            face_names = []
            for id in face_id:
                for people in faces.know_people:
                    if people.id == id:
                        name = people.name
                        face_names.append(name)
                        continue
                if id is None:
                    face_names.append("Unknown")
                        
                    
            faces_data = []
            # Costruiamo un oggetto completo per ogni volto rilevato
            # (top, right, bottom, left) sono le coordinate restituite da face_recognition
            for (top, right, bottom, left), name, id in zip(face_locations, face_names, face_id):
                person_data = None

                if id is not None:
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
                        "surname": "Unknown",
                        "age": 0,
                        "relationship": "Unknown",
                        "role": "unknown",
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
        logger.critical(f"Errore WebSocket: {e}")