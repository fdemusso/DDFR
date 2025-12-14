import logging
import sys
import numpy as np
import cv2

import insightface
from insightface.app import FaceAnalysis
import onnxruntime as ort

import utils.img as img
from models.person import Person

# --- FAISS SETUP (Auto-detection) ---
try:
    import faiss
    FAISS_AVAILABLE = True
    
    # Tentativo preliminare di verificare se la libreria supporta la GPU
    # (Non istanziamo ancora risorse pesanti, verifichiamo solo l'importabilità)
    try:
        # Questo test serve a capire se 'faiss-gpu' è installato e funzionante
        # Se siamo su faiss-cpu, StandardGpuResources solleverà un'eccezione
        res = faiss.StandardGpuResources()
        test_index = faiss.IndexFlatIP(128)
        faiss.index_cpu_to_gpu(res, 0, test_index)
        FAISS_GPU_AVAILABLE = True
    except AttributeError:
        # Se manca StandardGpuResources, è sicuramente la versione CPU
        FAISS_GPU_AVAILABLE = False
    except Exception:
        # Altri errori (es. driver CUDA mancanti)
        FAISS_GPU_AVAILABLE = False
        
except ImportError:
    FAISS_AVAILABLE = False
    FAISS_GPU_AVAILABLE = False

MODEL = "buffalo_l"
DETECTION_SIZE = 640

logger = logging.getLogger(__name__)

class FaceEngine:
    def __init__(self, people : list):
        self.FeatureMatrix : np.ndarray | None = None
        self.user_map: list[Person] = []
        self.index = None
        self.app = self._initialize_model(people)


    def _initialize_faiss_index(self, enable_gpu=False):
        if not FAISS_AVAILABLE or self.FeatureMatrix is None:
            return

        d = self.FeatureMatrix.shape[1]
        
        cpu_index = faiss.IndexFlatIP(d)
        cpu_index.add(self.FeatureMatrix.astype(np.float32))

        # Tentativo passaggio a GPU (solo se richiesto e disponibile)
        if enable_gpu and FAISS_GPU_AVAILABLE:
            try:
                # Risorse GPU standard (necessarie per FAISS GPU)
                self.gpu_resources = faiss.StandardGpuResources()
                
                # Sposta l'indice dalla RAM (CPU) alla VRAM (GPU)
                self.index = faiss.index_cpu_to_gpu(self.gpu_resources, 0, cpu_index)
                logger.info(f"FAISS: Indice spostato su GPU (CUDA attiva)")
            except Exception as e:
                logger.warning(f"FAISS GPU fallito (fallback su CPU): {e}")
                self.index = cpu_index
        else:
            self.index = cpu_index
            mode = "CPU (Forzata)" if not enable_gpu else "CPU (GPU non disp.)"
            logger.info(f"FAISS: Indice creato su {mode}")
        
    def _initialize_model(self, people):
        available_providers = ort.get_available_providers()
        providers_list = []
        
        using_cuda = False

        if 'CUDAExecutionProvider' in available_providers:
            providers_list.append('CUDAExecutionProvider')
            using_cuda = True
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
            self._initialize_faiss_index(using_cuda)
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
        # Controllo Database
        if self.FeatureMatrix is None:
            logger.warning("FeatureMatrix è None: database vuoto o non inizializzato")
            n_items = len(target_data) if isinstance(target_data, list) else 1
            return [(None, 0.0)] * n_items

        # Preparazione Input (Matrice N x D)
        if isinstance(target_data, list) and len(target_data) > 0 and isinstance(target_data[0], np.ndarray):
            input_matrix = np.stack(target_data)
        else:
            input_matrix = np.array(target_data, dtype=np.float32)
        
        if input_matrix.ndim == 1:
            input_matrix = input_matrix.reshape(1, -1)

        # Importante: FAISS vuole float32
        input_matrix = input_matrix.astype(np.float32)

        # Normalizzazione L2
        norms = np.linalg.norm(input_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        normalized_matrix = input_matrix / norms

        # --- FAISS vs NUMPY ---
        best_indices = None
        best_scores = None

        # Controllo se self.index esiste (creato da _initialize_faiss_index)
        if getattr(self, 'index', None) is not None:
            # k=1 significa "trova solo il più simile"
            scores, indices = self.index.search(normalized_matrix, k=1)
            
            # Appiattiamo i risultati (da matrice Nx1 a vettori N)
            best_scores = scores.flatten()
            best_indices = indices.flatten()
        else:
            # PERCORSO NUMPY
            all_scores = np.dot(normalized_matrix, self.FeatureMatrix.T)
            best_indices = np.argmax(all_scores, axis=1)
            best_scores = np.max(all_scores, axis=1)

        # Formattazione Risultati
        results = []
        for idx, score in zip(best_indices, best_scores):
            idx = int(idx)     # Cast a int nativo Python
            score = float(score) # Cast a float nativo Python

            if score > threshold:
                if idx < len(self.user_map):
                    results.append((self.user_map[idx], score))
                else:
                    logger.error(f"Index {idx} fuori range user_map")
                    results.append((None, score))
            else:
                results.append((None, score))
        
        return results

