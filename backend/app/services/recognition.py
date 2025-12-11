import logging
import sys
import numpy as np
import cv2

import insightface
from insightface.app import FaceAnalysis
import onnxruntime as ort

import utils.img as img
import models.person as p

MODEL = "buffalo_l"
DETECTION_SIZE = 640

logger = logging.getLogger(__name__)

class FaceEngine:
    def __init__(self, people : list):
        self.app = self._initialize_model(people)

        # Informazioni su tutte le persone del database
        self.feature_matrix = None
        self.user_map = []
        
    def _initialize_model(self, people):

        logger.info("--- INIZIALIZZAZIONE MOTORE AI ---")
        
        # Rilevazione del Hardware
        available_providers = ort.get_available_providers()
        logger.info(f"Hardware Rilevato: {available_providers}")
        
        providers_list = []
        
        # CASO A: NVIDIA (Windows/Linux con GPU)
        if 'CUDAExecutionProvider' in available_providers:
            providers_list.append('CUDAExecutionProvider')
            logger.info(">>> MODO: NVIDIA CUDA (Massima Potenza)")

        # CASO B: MAC (Apple Silicon M1/M2/M3)
        elif 'CoreMLExecutionProvider' in available_providers:
            # CoreML usa il Neural Engine del Mac
            providers_list.append('CoreMLExecutionProvider') 
            logger.info(">>> MODO: APPLE COREML (Mac Silicon)")
            
        # CASO C: WINDOWS STANDARD (AMD / Intel Integrata)
        elif 'DmlExecutionProvider' in available_providers:
            providers_list.append('DmlExecutionProvider')
            logger.info(">>> MODO: DIRECTML (Accelerazione Windows)")

        # CASO D: CPU (Fallback di sicurezza)
        providers_list.append('CPUExecutionProvider')
        
        try:

            model = FaceAnalysis(name=MODEL, providers=providers_list)
            model.prepare(ctx_id=0, det_size=(DETECTION_SIZE, DETECTION_SIZE))
            logger.info("Modello InsightFace caricato con successo!")
            
            
        except Exception as e:
            logger.critical(f"Impossibile avviare il modello : {e}")
            sys.exit(1) #WARNING: fa crashare il backend all avvio se non riesce a capire l hardware
        
        logger.info("--- DOWNLOAD DELLE PERSONE DAL DATABASE ---")

        all_embeddings = []
        self.user_map = []
        for person in people:
            for hash, vector in person.encoding.items():
                np_vector = np.array(vector, dtype=np.float32)
                all_embeddings.append(np_vector)
                self.user_map.append(str(person.id))
        if len(all_embeddings) > 0:
            self.feature_matrix = np.vstack(all_embeddings)
            logger.debug(f"Database caricato: {self.feature_matrix.shape[0]} volti totali.")
        else:
            self.feature_matrix = None
            logger.debug("Database vuoto.")
        return model

    def analyze_frame(self, frame_bgr: np.ndarray):

        if frame_bgr is None:
            return []
        
        faces = self.app.get(frame_bgr)
        return faces
    


    def compare_embeddings(self, known_embeddings, target_embedding, threshold=0.5):

        sims = np.dot(known_embeddings, target_embedding)
        
        # Trova il punteggio più alto
        best_idx = np.argmax(sims)
        max_score = sims[best_idx]
        
        if max_score > threshold:
            return best_idx, max_score
        
        return None, max_score



engine = FaceEngine()