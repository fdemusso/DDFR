from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import logging
import base64
import json

from insightface.app.common import Face
from models.person import Person
from typing import List, Tuple, Optional

from config import database_settings as set, api_settings
from services import database
import services.recognition as fr

logger = logging.getLogger(__name__)
router = APIRouter()

DATASET = database.Database(
    url=set.url,
    name=set.name,
    collection=set.collection,
)
people = DATASET.get_all_people()
engine = fr.FaceEngine(people)

if engine.FeatureMatrix is None:
    logger.error(f"FeatureMatrix None dopo inizializzazione. Persone caricate: {len(people)}")   

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()

            try:
                if ',' in data:
                    encoded = data.split(",", 1)[1]
                else:
                    encoded = data
                
                image_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    continue
            except Exception as e:
                logger.error(f"Errore parsing immagine: {e}")
                continue

            faces: List[Face] = engine.analyze_frame(frame)
            found_people_list: List[Tuple[Optional[Person], Face]] = []

            if engine.FeatureMatrix is not None:
                for face in faces:
                    found_person, score = engine.identify(face.embedding, threshold=0.4)
                    found_people_list.append((found_person, face))
            else:
                logger.error(f"FeatureMatrix None ma rilevati {len(faces)} volti")
                for face in faces:
                    found_people_list.append((None, face))

            faces_data = []
            
            for person_data, face in found_people_list:
                bbox = face.bbox.astype(int)
                left, top, right, bottom = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

                face_dict = {
                    "id": f"{top}_{left}",
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                }

                if person_data is not None:
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
                    face_dict.update({
                        "name": "Unknown",
                        "surname": None,
                        "age": 0,
                        "relationship": None,
                        "role": None,
                    })

                faces_data.append(face_dict)

            await websocket.send_text(json.dumps({"status": "ok", "faces": faces_data}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.critical(f"Errore critico WebSocket: {e}", exc_info=True)