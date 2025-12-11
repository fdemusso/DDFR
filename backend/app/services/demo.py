## DEMO DEL CODICE DI RICONOSCIMENTO CON QUESTA NUOVA LIBRERIA


import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import onnxruntime as ort
import time
import sys

# =============================================================================
# 1. CLASSE GESTIONE HARDWARE (Il "Motore")
# =============================================================================
class AI_Engine:
    def __init__(self):
        self.model = self._setup_hardware()

    def _setup_hardware(self):
        """
        Rileva automaticamente se sei su Mac, NVIDIA o PC standard
        e carica il driver (Provider) giusto per ONNX Runtime.
        """
        print("\n--- INIZIALIZZAZIONE HARDWARE ---")
        available_providers = ort.get_available_providers()
        print(f"Driver disponibili: {available_providers}")

        providers_list = []
        
        # Ordine di preferenza per le prestazioni
        if 'CUDAExecutionProvider' in available_providers:
            providers_list.append('CUDAExecutionProvider') # NVIDIA GPU
            print(">>> ✅ MODO: GPU NVIDIA (Massima Velocità)")
        elif 'CoreMLExecutionProvider' in available_providers:
            providers_list.append('CoreMLExecutionProvider') # MAC M1/M2/M3
            print(">>> ✅ MODO: APPLE COREML (Mac Silicon)")
        elif 'DmlExecutionProvider' in available_providers:
            providers_list.append('DmlExecutionProvider') # Windows AMD/Intel
            print(">>> ✅ MODO: DIRECTML (Accelerazione Windows)")
        else:
            providers_list.append('CPUExecutionProvider') # CPU Standard
            print(">>> ⚠️ MODO: CPU (Fallback - Potrebbe essere lento)")

        # Carichiamo il modello "buffalo_l".
        # Include: Detection, Recognition, Gender (Sesso), Age (Età), Landmarks (Punti chiave)
        app = FaceAnalysis(name='buffalo_l', providers=providers_list)
        
        # det_size=(640, 640): Fissa la dimensione di analisi. 
        # Più è basso, più è veloce. Più è alto, più vede volti piccoli/lontani.
        app.prepare(ctx_id=0, det_size=(640, 640))
        return app

    def get_faces(self, frame):
        """Analizza il frame e restituisce una lista di oggetti 'Face'"""
        return self.model.get(frame)


# =============================================================================
# 2. CLASSE DATABASE SIMULATO (La "Memoria")
# =============================================================================
class FaceDatabase:
    def __init__(self):
        # Struttura:
        # {
        #    "Mario Rossi": [array_embedding_1, array_embedding_2],
        #    "Luigi Verdi": [array_embedding_1]
        # }
        # Supportiamo più vettori per la stessa persona per aumentare la precisione.
        self.known_people = {}

    def register_user(self, name, image_path, engine):
        """
        Legge un'immagine dal disco, trova il volto e salva la sua 'impronta digitale' (embedding).
        """
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Errore: Impossibile leggere {image_path}")
            return

        faces = engine.get_faces(img)
        if len(faces) == 0:
            print(f"❌ Errore: Nessun volto trovato in {image_path}")
            return
        
        # Prendiamo il volto più grande trovato nella foto di registrazione
        # (Ordiniamo per area del bounding box: (right-left) * (bottom-top))
        primary_face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]))
        
        # L'embedding è un vettore di 512 numeri float che rappresenta la faccia
        embedding = primary_face.embedding

        # Aggiungiamo al database
        if name not in self.known_people:
            self.known_people[name] = []
        
        self.known_people[name].append(embedding)
        print(f"✅ Registrato: {name} (da {image_path})")

    def identify_face(self, target_embedding, threshold=0.5):
        """
        Confronta il volto target con TUTTI i volti nel database.
        Restituisce il nome migliore e il punteggio di somiglianza.
        """
        best_name = "Sconosciuto"
        best_score = 0.0

        for name, embeddings_list in self.known_people.items():
            for known_emb in embeddings_list:
                # --- IL CUORE MATEMATICO ---
                # Calcoliamo la 'Cosine Similarity' tramite Prodotto Scalare (Dot Product).
                # I vettori di InsightFace sono già normalizzati, quindi basta np.dot.
                # Risultato: un numero da -1 a 1. Più vicino a 1 = Più simile.
                score = np.dot(known_emb, target_embedding)

                if score > best_score:
                    best_score = score
                    if score > threshold:
                        best_name = name
        
        return best_name, best_score


# =============================================================================
# 3. LOOP PRINCIPALE (Il "Programma")
# =============================================================================
def main():
    # 1. Avvia il motore AI
    engine = AI_Engine()
    
    # 2. Crea il database vuoto
    db = FaceDatabase()

    # --- REGISTRAZIONE MANUALE (Modifica qui per testare!) ---
    # db.register_user("Tuo Nome", "foto_tua.jpg", engine)
    # db.register_user("Tuo Nome", "altra_foto_tua_diversa_luce.jpg", engine)
    # db.register_user("Elon Musk", "elon.jpg", engine)
    
    # Esempio: Se non hai foto, il codice gira lo stesso ma ti chiamerà "Sconosciuto"
    print("\nAvvio Webcam... (Premi 'Q' per uscire)")
    
    cap = cv2.VideoCapture(0) # 0 è la webcam di default
    
    # Per calcolare gli FPS
    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # InsightFace lavora nativamente in BGR (formato OpenCV standard)
        # Non serve convertire colori o ridimensionare manualmente!
        
        # --- FASE 1: RICONOSCIMENTO ---
        t0 = time.time()
        faces = engine.get_faces(frame)
        t1 = time.time()
        inference_time = (t1 - t0) * 1000 # millisecondi

        # --- FASE 2: DISEGNO SULLO SCHERMO ---
        for face in faces:
            # bbox è un array [x1, y1, x2, y2]
            box = face.bbox.astype(int)
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]

            # IDENTIFICAZIONE
            name, score = db.identify_face(face.embedding, threshold=0.5)

            # EXTRA DI INSIGHTFACE: Genere ed Età
            # face.sex = 1 (Maschio), 0 (Femmina) solitamente, ma dipende dal modello.
            # In 'buffalo_l': 0=F, 1=M.
            gender = "M" if face.sex == 1 else "F"
            age = int(face.age)

            # Scegliamo il colore (Verde se conosciuto, Rosso se sconosciuto)
            color = (0, 255, 0) if name != "Sconosciuto" else (0, 0, 255)

            # Disegna il rettangolo
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Scrittura Info (Nome, Score, Sesso, Età)
            label = f"{name} ({score:.2f})"
            sub_label = f"Sex: {gender}, Age: {age}"
            
            # Sfondo nero per il testo (per leggibilità)
            cv2.rectangle(frame, (x1, y1 - 40), (x2, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, sub_label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # EXTRA: Punti Chiave (Landmarks)
            # kps è una lista di 5 punti (Occhio DX, Occhio SX, Naso, Bocca DX, Bocca SX)
            if face.kps is not None:
                for kp in face.kps:
                    kp = kp.astype(int)
                    # Disegna pallini azzurri sui punti chiave
                    cv2.circle(frame, (kp[0], kp[1]), 3, (255, 255, 0), -1)

        # Calcolo FPS
        frame_count += 1
        elapsed = time.time() - start_time
        if elapsed > 1.0:
            fps = frame_count / elapsed
            print(f"FPS: {fps:.2f} | Volti: {len(faces)} | Inferenza: {inference_time:.1f}ms")
            frame_count = 0
            start_time = time.time()

        cv2.imshow('InsightFace Demo Monolite', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()