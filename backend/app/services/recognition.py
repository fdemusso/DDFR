import logging
import sys
import numpy as np
import cv2

import insightface
from insightface.app import FaceAnalysis
import onnxruntime as ort

import utils.img as img
from models.person import Person

MODEL = "buffalo_l"
DETECTION_SIZE = 640

logger = logging.getLogger(__name__)

class FaceEngine:
    def __init__(self, people : list):
        self.FeatureMatrix : np.ndarray | None = None
        self.user_map: list[Person] = []
        self.app = self._initialize_model(people)
        
    def _initialize_model(self, people):
        available_providers = ort.get_available_providers()
        providers_list = []
        
        if 'CUDAExecutionProvider' in available_providers:
            providers_list.append('CUDAExecutionProvider')
        elif 'CoreMLExecutionProvider' in available_providers:
            providers_list.append('CoreMLExecutionProvider') 
        elif 'DmlExecutionProvider' in available_providers:
            providers_list.append('DmlExecutionProvider')
        
        providers_list.append('CPUExecutionProvider')
        
        try:
            model = FaceAnalysis(name=MODEL, providers=providers_list)
            model.prepare(ctx_id=0, det_size=(DETECTION_SIZE, DETECTION_SIZE))
        except Exception as e:
            logger.critical(f"Impossibile avviare il modello: {e}")
            sys.exit(1)

        AllEmbeddings = []
        self.user_map = []
        embedding_dimension = None
        
        for person in people:
            if person.encoding is None or not person.encoding:
                continue
            
            for hash, vector in person.encoding.items():
                try:
                    if vector is None or not isinstance(vector, (list, np.ndarray)) or len(vector) == 0:
                        continue
                    
                    np_vector = np.array(vector, dtype=np.float32)
                    if np_vector.ndim > 1:
                        np_vector = np_vector.flatten()
                    
                    if embedding_dimension is None:
                        embedding_dimension = len(np_vector)
                    elif len(np_vector) != embedding_dimension:
                        logger.error(f"Embedding con dimensione errata per {person.name} {person.surname} (hash: {hash})")
                        continue
                    
                    if np.any(np.isnan(np_vector)) or np.any(np.isinf(np_vector)):
                        logger.error(f"Embedding con valori NaN/Inf per {person.name} {person.surname} (hash: {hash})")
                        continue
                    
                    AllEmbeddings.append(np_vector)
                    self.user_map.append(person)
                except Exception as e:
                    logger.error(f"Errore nel processare encoding per {person.name} {person.surname} (hash: {hash}): {e}")
                    continue

        if len(AllEmbeddings) > 0:
            self.FeatureMatrix = np.vstack(AllEmbeddings)
            if len(self.user_map) != self.FeatureMatrix.shape[0]:
                logger.error(f"ERRORE CRITICO: Dimensione user_map ({len(self.user_map)}) non corrisponde a FeatureMatrix ({self.FeatureMatrix.shape[0]})")
                raise ValueError("Inconsistenza tra user_map e FeatureMatrix")
            if np.any(np.isnan(self.FeatureMatrix)) or np.any(np.isinf(self.FeatureMatrix)):
                logger.error("FeatureMatrix contiene valori NaN o Inf!")
            
            # Pre-normalizza la FeatureMatrix una volta sola (ottimizzazione prestazioni)
            feature_norms = np.linalg.norm(self.FeatureMatrix, axis=1, keepdims=True)
            feature_norms[feature_norms == 0] = 1.0
            self.FeatureMatrix = self.FeatureMatrix / feature_norms
            logger.info(f"FeatureMatrix pre-normalizzata: {self.FeatureMatrix.shape[0]} embeddings")
        else:
            self.FeatureMatrix = None
            logger.warning("Database vuoto: nessun encoding trovato.")
        return model

    def analyze_frame(self, frame_bgr: np.ndarray):

        if frame_bgr is None:
            return []
        
        faces = self.app.get(frame_bgr)
        return faces
    
    def analyze_img(self, path):
        pic = img.ImgValidation(path, delete=True)

        if pic.path is None:
            return None
        
        face = self.analyze_frame(cv2.imread(pic.path))

        if len(face) == 0:
            return None
        
        # Seleziona il volto più grande in caso di più volti
        primary_face = max(face, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]))
        embedding_list = primary_face.embedding.tolist()

        return {pic.hash : embedding_list}
    
    def identify(self, target_data, threshold=0.5):
        if self.FeatureMatrix is None:
            logger.warning("FeatureMatrix è None: database vuoto o non inizializzato")
            n_items = len(target_data) if isinstance(target_data, list) else 1
            return [(None, 0.0)] * n_items

        if isinstance(target_data, list) and len(target_data) > 0 and isinstance(target_data[0], np.ndarray):
            input_matrix = np.stack(target_data)
        else:
            input_matrix = np.array(target_data, dtype=np.float32)
       
        
        if input_matrix.ndim == 1:
            input_matrix = input_matrix.reshape(1, -1)

        # Normalizzazione L2 (Vettorializzata)
        norms = np.linalg.norm(input_matrix, axis=1, keepdims=True)
        # Evito la divisone per 0
        norms[norms == 0] = 1e-10
        normalized_matrix = input_matrix / norms

        all_scores = np.dot(normalized_matrix, self.FeatureMatrix.T)
        
        best_indices = np.argmax(all_scores, axis=1)   
        best_scores = np.max(all_scores, axis=1)
        
        results = []
        for idx, score in zip(best_indices, best_scores):
            if score > threshold:
                if idx < len(self.user_map):
                    results.append((self.user_map[idx], float(score))) # lista di persona : punteggio
                else:
                    logger.error(f"Index {idx} fuori range user_map")
                    results.append((None, float(score)))
            else:
                results.append((None, float(score)))
        
        return results

