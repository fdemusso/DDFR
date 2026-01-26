from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import os
import cv2
# Limitiamo i problemi che può causare il Multithreading a numpy
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np
import logging

import asyncio
from concurrent.futures import ThreadPoolExecutor

from insightface.app.common import Face
from models.person import Person
from typing import List, Tuple, Optional

import services.recognition as fr

from . import route

logger = logging.getLogger(__name__)
router = APIRouter()

executor = ThreadPoolExecutor(max_workers=1)

def process_image_sync(image_bytes: bytes) -> dict | None:
    """Process image bytes synchronously for face detection and recognition.

    Decodes image bytes, detects faces, and identifies persons using the face engine.
    Returns face detection results with bounding boxes and person information.

    Args:
        image_bytes (bytes): Raw image bytes to process.

    Returns:
        dict | None: Dictionary containing status and list of detected faces.
            Format: {"status": "ok", "faces": [{"id": str, "top": int, "right": int, 
            "bottom": int, "left": int, "name": str, "surname": str, "age": int,
            "relationship": str, "role": str}, ...]}
            Returns None if image decoding fails.

    """
    engine = route.get_engine()
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return None
    except Exception as e:
        logger.error(f"Errore parsing immagine: {e}")
        return None

    faces: List[Face] = engine.analyze_frame(frame)
    found_people_list: List[Tuple[Optional[Person], Face]] = []

    # Nessun volto rilevato (uscita rapida)
    if not faces:
        return {"status": "ok", "faces": []}

    # Abbiamo volti E il Database è attivo -> BATCH PROCESSING
    if engine.feature_matrix is not None:
        embeddings = [face.embedding for face in faces]
        identities = engine.identify(embeddings, threshold=0.4)
        
        for (found_person, score), face in zip(identities, faces):
            found_people_list.append((found_person, face))
            
    # Abbiamo volti MA il Database non c'è (Fallback)
    else:
        logger.error(f"feature_matrix None ma rilevati {len(faces)} volti")
        for face in faces:
            found_people_list.append((None, face))

    faces_data = []
    
    # Ottieni dimensioni frame per validazione coordinate
    frame_height, frame_width = frame.shape[:2]
    logger.info(f"Frame processato: {frame_width}x{frame_height} (aspect ratio: {frame_width/frame_height:.2f})")
    
    for person_data, face in found_people_list:
        bbox = face.bbox.astype(int)
        left, top, right, bottom = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        
        # Log dettagliato per debug coordinate
        logger.info(f"Bbox InsightFace: {bbox} -> left={left}, top={top}, right={right}, bottom={bottom}")
        logger.info(f"  Dimensioni bbox: width={right-left}, height={bottom-top}")
        logger.info(f"  Posizione: center_x={(left+right)/2:.1f}, center_y={(top+bottom)/2:.1f}")
        
        # Validazione coordinate (devono essere dentro il frame)
        if left < 0 or top < 0 or right > frame_width or bottom > frame_height:
            logger.warning(f"Coordinate bbox fuori range: left={left}, top={top}, "
                         f"right={right}, bottom={bottom}, frame={frame_width}x{frame_height}")
            # Clamp coordinate ai limiti del frame
            left = max(0, min(left, frame_width - 1))
            top = max(0, min(top, frame_height - 1))
            right = max(left + 1, min(right, frame_width))
            bottom = max(top + 1, min(bottom, frame_height))
            logger.info(f"  Coordinate dopo clamp: left={left}, top={top}, right={right}, bottom={bottom}")

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

    return {"status": "ok", "faces": faces_data}
        
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time face recognition.

    Accepts binary image data over WebSocket connection, processes frames
    asynchronously for face detection and recognition, and returns results in JSON format.
    Rate limiting is handled on the frontend (50ms = 20 FPS).

    Args:
        websocket (WebSocket): FastAPI WebSocket connection instance.

    Raises:
        WebSocketDisconnect: When client disconnects from the WebSocket.
        Exception: Logs any errors during image processing or WebSocket communication.

    """
    await websocket.accept()
    loop = asyncio.get_event_loop()

    try:
        while True:
            data = await websocket.receive_bytes()
            
            # Il rate limiting è gestito lato frontend (50ms = 20 FPS)
            result = await loop.run_in_executor(executor, process_image_sync, data)

            # Invia sempre una risposta per sbloccare il frontend (isProcessing).
            # Se result è None (decode fallito) inviamo comunque {"status":"ok","faces":[]}.
            payload = result if result is not None else {"status": "ok", "faces": []}
            await websocket.send_json(payload)

    except WebSocketDisconnect:
        logger.info("Client disconnesso")
    except Exception as e:
        logger.error(f"Errore WebSocket: {e}")