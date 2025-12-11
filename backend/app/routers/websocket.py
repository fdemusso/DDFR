from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import logging
import base64
import json
import time

# Import corretti per la tipizzazione
from insightface.app.common import Face
from models.person import Person
from typing import List, Tuple, Optional

from config import database_settings as set, api_settings
from services import database
import services.recognition as fr

# Configurazione iniziale
logger = logging.getLogger(__name__)
router = APIRouter()

# Caricamento SINGOLO all'avvio 
DATASET = database.Database(
    url=set.url,
    name=set.name,
    collection=set.collection,
)
people = DATASET.get_all_people() 
engine = fr.FaceEngine(people)   

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Client WebSocket connesso da {websocket.client}")

    try:
        while True:
            # Ricezione dati
            data = await websocket.receive_text()

            # Parsing Immagine (Base64 -> OpenCV)
            try:
                if ',' in data:
                    encoded = data.split(",", 1)[1] # Ottimizzato: prendiamo subito la parte dopo la virgola
                else:
                    encoded = data
                
                # frombuffer è rapidissimo
                image_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    continue
            except Exception as e:
                logger.error(f"Errore parsing immagine: {e}")
                continue

            # t0 = time.time() # Scommenta per debuggare le performance
            
            # Restituisce una lista di oggetti Face. Se vuota, faces = []
            faces: List[Face] = engine.analyze_frame(frame)
            
            # t1 = time.time()
            # logger.info(f"Inference: {(t1-t0)*1000:.1f}ms - Volti: {len(faces)}")

            # Identificazione
            # Creiamo una lista vuota per QUESTO frame specifico
            found_people_list: List[Tuple[Optional[Person], Face]] = []

            # Controllo di sicurezza se il motore è pronto
            if engine.feature_matrix is not None:
                for face in faces:
                    # Identify restituisce (Person Object, score) oppure (None, score)
                    found_person, score = engine.identify(face.embedding, threshold=0.5)
                    
                    
                    found_people_list.append((found_person, face))
            else:
                # Se il DB è vuoto ma vedo facce, le aggiungo come sconosciuti
                for face in faces:
                    found_people_list.append((None, face))

            # Costruzione JSON Risposta
            faces_data = []
            
            for person_data, face in found_people_list:
                

                bbox = face.bbox.astype(int)
                left, top, right, bottom = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

                face_dict = {
                    "id": f"{top}_{left}", # ID temporaneo per il frontend
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left#,
                    #  Extra di InsightFace
                    # "sex": "M" if face.sex == 1 else "F",
                    # "age": int(face.age)
                }

                if person_data is not None:
                    # --- CONOSCIUTO ---
                    relationship = getattr(person_data.relationship, "value", person_data.relationship)
                    role = getattr(person_data.role, "value", person_data.role)

                    face_dict.update({
                        "name": person_data.name,
                        "surname": person_data.surname,
                        "age": person_data.age, 
                        "relationship": relationship,
                        "role": role,
                    })
                else:
                    # --- SCONOSCIUTO ---
                    face_dict.update({
                        "name": "Unknown",
                        "surname": None,
                        "age": 0,
                        "relationship": None,
                        "role": None,
                    })

                faces_data.append(face_dict)

            # 6. Invio al Client
            await websocket.send_text(json.dumps({"status": "ok", "faces": faces_data}))

    except WebSocketDisconnect:
        logger.info("Client WebSocket disconnesso")
    except Exception as e:
        logger.critical(f"Errore Critico WebSocket: {e}", exc_info=True)