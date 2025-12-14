import logging
import sys
import os
import numpy as np
import cv2
from typing import Optional

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
    """Face recognition engine using InsightFace and FAISS for similarity search.

    Manages face detection, embedding extraction, and person identification
    using pre-trained models and efficient vector similarity search.

    Attributes:
        feature_matrix (np.ndarray | None): Normalized matrix of face embeddings.
        user_map (list[Person]): List of Person objects corresponding to embeddings.
        index: FAISS index for fast similarity search (optional).
        app: InsightFace FaceAnalysis model instance.

    """

    def __init__(self, people : list):
        """Initialize FaceEngine with person data.

        Args:
            people (list): List of Person objects with face encodings to initialize the engine.

        """
        self.feature_matrix : np.ndarray | None = None
        self.user_map: list[Person] = []
        self.index = None
        self.app = self._initialize_model(people)


    def _initialize_faiss_index(self, enable_gpu=False):
        """Initialize FAISS index for fast similarity search.

        Creates FAISS index from feature matrix, optionally using GPU acceleration
        if available and requested.

        Args:
            enable_gpu (bool): Whether to attempt GPU acceleration. Default: False.

        """
        if not FAISS_AVAILABLE or self.feature_matrix is None:
            return

        d = self.feature_matrix.shape[1]
        
        cpu_index = faiss.IndexFlatIP(d)
        cpu_index.add(self.feature_matrix.astype(np.float32))

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
        """Initialize InsightFace model and build feature matrix from people data.

        Selects best available execution provider (CUDA, CoreML, DML, or CPU),
        initializes the face analysis model, and builds normalized feature matrix
        from person encodings. Initializes FAISS index if embeddings are available.

        Args:
            people (list): List of Person objects with encodings.

        Returns:
            FaceAnalysis: Initialized InsightFace model instance.

        Raises:
            SystemExit: If model initialization fails.
            ValueError: If feature matrix and user_map dimensions don't match.

        """
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

        all_embeddings = []
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
                    
                    all_embeddings.append(np_vector)
                    self.user_map.append(person)
                except Exception as e:
                    logger.error(f"Errore nel processare encoding per {person.name} {person.surname} (hash: {hash}): {e}")
                    continue

        if len(all_embeddings) > 0:
            self.feature_matrix = np.vstack(all_embeddings)
            if len(self.user_map) != self.feature_matrix.shape[0]:
                logger.error(f"ERRORE CRITICO: Dimensione user_map ({len(self.user_map)}) non corrisponde a feature_matrix ({self.feature_matrix.shape[0]})")
                raise ValueError("Inconsistenza tra user_map e feature_matrix")
            if np.any(np.isnan(self.feature_matrix)) or np.any(np.isinf(self.feature_matrix)):
                logger.error("feature_matrix contiene valori NaN o Inf!")
            
            # Pre-normalizza la feature_matrix una volta sola (ottimizzazione prestazioni)
            feature_norms = np.linalg.norm(self.feature_matrix, axis=1, keepdims=True)
            feature_norms[feature_norms == 0] = 1.0
            self.feature_matrix = self.feature_matrix / feature_norms
            logger.info(f"feature_matrix pre-normalizzata: {self.feature_matrix.shape[0]} embeddings")
            self._initialize_faiss_index(using_cuda)
        else:
            self.feature_matrix = None
            logger.warning("Database vuoto: nessun encoding trovato.")
        return model

    def analyze_frame(self, frame_bgr: np.ndarray) -> list:
        """Detect and extract face embeddings from a BGR frame.

        Args:
            frame_bgr (np.ndarray): Input image frame in BGR format.

        Returns:
            list: List of Face objects with detected faces and embeddings.
                Returns empty list if frame is None or no faces detected.

        """
        if frame_bgr is None:
            return []
        
        faces = self.app.get(frame_bgr)
        return faces
    
    def analyze_img(self, path: str | os.PathLike) -> dict | None:
        """Analyze an image file and extract face embedding.

        Validates and normalizes the image, detects faces, and extracts
        embedding from the largest detected face.

        Args:
            path: Path to image file (Path object or string).

        Returns:
            dict | None: Dictionary mapping image hash to embedding list, or None if
                no valid face detected.

        """
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
    
    def identify(self, target_data: np.ndarray | list[np.ndarray], threshold: float = 0.5) -> list[tuple[Optional[Person], float]]:
        """Identify persons from face embeddings using similarity search.

        Uses FAISS index (if available) or numpy dot product to find the most
        similar person embeddings. Returns matches above the similarity threshold.

        Args:
            target_data: Single embedding (np.ndarray) or list of embeddings to identify.
            threshold (float): Minimum similarity score (0.0-1.0) to consider a match.
                Default: 0.5.

        Returns:
            list[tuple[Optional[Person], float]]: List of tuples (Person, score) for each input embedding.
                Returns (None, score) if no match above threshold found.

        """
        # Controllo Database
        if self.feature_matrix is None:
            logger.warning("feature_matrix è None: database vuoto o non inizializzato")
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
            all_scores = np.dot(normalized_matrix, self.feature_matrix.T)
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

