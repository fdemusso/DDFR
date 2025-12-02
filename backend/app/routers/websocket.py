from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import logging
import base64
import json

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
logger.info(f"Caricati {len(faces.known_face_names)} volti noti dal database.")

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
                face_names = []
                for face_encoding in face_encodings:
                    # Confronto con i volti noti
                    matches = fr.face_recognition.compare_faces(faces.known_face_encodings, face_encoding, tolerance=0.6)
                    name = "Sconosciuto"

                    # Uso il volto più simile
                    face_distances = fr.face_recognition.face_distance(faces.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = faces.known_face_names[best_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame 

            faces_data = []
            for (top, right, bottom, left) in face_locations:
                # 5. Ri-scaliamo le coordinate x4
                faces_data.append({
                    "id": f"{top}_{left}", 
                    "name": name, 
                    "top": top * 4,
                    "right": right * 4,
                    "bottom": bottom * 4,
                    "left": left * 4
                })

            # 6. Risposta
            await websocket.send_text(json.dumps({"status": "ok", "faces": faces_data}))

    except WebSocketDisconnect:
        logger.info("Client WebSocket disconnesso")
    except Exception as e:
        logger.critical(f"Errore WebSocket: {e}")