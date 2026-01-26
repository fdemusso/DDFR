import React, { useRef, useState, useMemo, useEffect } from 'react';
import './App.css';

// Custom Hooks
import { useWebSocket } from './hooks/useWebSocket';
import { useWebcam } from './hooks/useWebcam';
import { useFaceDetection } from './hooks/useFaceDetection';
import { useLatency } from './hooks/useLatency';

// Constants
import { CAPTURE_WIDTH, CAPTURE_HEIGHT, getApiUrl } from './utils/constants';

// Componenti
import WebcamView from './components/WebcamView';
import FaceBox from './components/FaceBox';
import StatusOverlay from './components/StatusOverlay';
import CameraToggle from './components/CameraToggle';
import DebugInfo from './components/DebugInfo';
import SetupWizard from './components/SetupWizard';
import AddPersonDialog from './components/AddPersonDialog';
import BetaBanner from './components/BetaBanner';
import { Button } from './components/ui/button';
import { UserPlus } from 'lucide-react';

const API_BASE_URL = getApiUrl();

function App() {
  const webcamRef = useRef(null);
  
  // Stati locali
  const [isFrontCamera, setIsFrontCamera] = useState(true);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [hasPatient, setHasPatient] = useState(null); // null = loading, true/false = loaded
  const [showAddPersonDialog, setShowAddPersonDialog] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(true);

  // Hook personalizzati per gestione faces
  const { faces, setFaces, framesSent, setFramesSent } = useFaceDetection();

  // Hook per tracking latenza
  const { latency, avgLatency, markSent, markReceived } = useLatency();

  // Handler per messaggi WebSocket
  const handleMessage = (data) => {
    markReceived(); // Marca ricezione risposta per calcolo latenza
    const rawFaces = Array.isArray(data.faces) ? data.faces : [];

    const parsedFaces = rawFaces.map((f) => {
      const name = (f.name || "").toString().trim();
      const surname = (f.surname || "").toString().trim();
      const fullNameRaw = [name, surname].filter(Boolean).join(" ").trim();

      let age = f.age;
      if (typeof age === "string") {
        const n = parseInt(age, 10);
        age = Number.isNaN(n) ? 0 : n;
      }

      return {
        ...f,
        fullName: fullNameRaw || "UNKNOWN",
        age,
      };
    });

    setFaces(parsedFaces);
    setFramesSent(prev => prev + 1);
  };

  // Hook WebSocket con riconnessione automatica
  const { ws, connectionStatus, isProcessing } = useWebSocket(handleMessage);

  // Hook per cattura e invio frame (con requestAnimationFrame)
  useWebcam(webcamRef, ws, isProcessing, markSent);

  // Stato per forzare il ricalcolo dello scaling quando le dimensioni cambiano
  const [videoDimensions, setVideoDimensions] = useState({ width: 0, height: 0, clientWidth: 0, clientHeight: 0 });
  
  // Effect per aggiornare le dimensioni del video quando cambiano
  useEffect(() => {
    if (!isCameraReady) return;
    
    const updateDimensions = () => {
      const videoEl = webcamRef.current?.video;
      if (videoEl && videoEl.videoWidth && videoEl.videoHeight && videoEl.clientWidth && videoEl.clientHeight) {
        setVideoDimensions({
          width: videoEl.videoWidth,
          height: videoEl.videoHeight,
          clientWidth: videoEl.clientWidth,
          clientHeight: videoEl.clientHeight
        });
      }
    };
    
    // Aggiorna immediatamente
    updateDimensions();
    
    // Aggiorna quando la finestra viene ridimensionata
    window.addEventListener('resize', updateDimensions);
    
    // Aggiorna periodicamente per catturare cambiamenti (es. fullscreen)
    const interval = setInterval(updateDimensions, 500);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
      clearInterval(interval);
    };
  }, [isCameraReady]);
  
  // Calcolo scale factors con useMemo (ottimizzazione)
  // Le coordinate dal backend sono basate sul frame ridimensionato (CAPTURE_WIDTH x CAPTURE_HEIGHT = 640x480)
  // Il frame viene catturato usando drawImage(video, 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT)
  // quindi le coordinate sono sempre relative a 640x480
  // Dobbiamo scalare dalle coordinate 640x480 alle dimensioni del video renderizzato VISIBILE
  const { scaleX, scaleY, offsetX, offsetY } = useMemo(() => {
    const videoEl = webcamRef.current?.video;
    if (!videoEl || !videoDimensions.width || !videoDimensions.height || !videoDimensions.clientWidth || !videoDimensions.clientHeight) {
      return { scaleX: 1, scaleY: 1, offsetX: 0, offsetY: 0 };
    }
    
    // Dimensioni del frame catturato (quello inviato al backend)
    const captureWidth = CAPTURE_WIDTH;  // 640
    const captureHeight = CAPTURE_HEIGHT; // 480
    
    // Dimensioni reali del video (usa lo stato per garantire che siano aggiornate)
    const videoWidth = videoDimensions.width;
    const videoHeight = videoDimensions.height;
    const videoAspect = videoWidth / videoHeight;
    
    // Dimensioni del contenitore (dove viene renderizzato il video)
    const containerWidth = videoDimensions.clientWidth;
    const containerHeight = videoDimensions.clientHeight;
    const containerAspect = containerWidth / containerHeight;
    
    // Calcola le dimensioni effettive del video renderizzato con object-fit: cover
    // object-fit: cover mantiene l'aspect ratio e riempie il contenitore, tagliando se necessario
    let renderedWidth, renderedHeight;
    if (videoAspect > containerAspect) {
      // Il video è più largo del contenitore -> viene scalato in base all'altezza
      renderedHeight = containerHeight;
      renderedWidth = containerHeight * videoAspect;
    } else {
      // Il video è più alto del contenitore -> viene scalato in base alla larghezza
      renderedWidth = containerWidth;
      renderedHeight = containerWidth / videoAspect;
    }
    
    // IMPORTANTE: Il frame viene catturato dal video originale usando drawImage(video, 0, 0, 640, 480)
    // Questo ridimensiona/stira il video originale a 640x480
    // Le coordinate dal backend sono relative a quel frame 640x480
    
    // Il video viene renderizzato con object-fit: cover, che riempie il contenitore
    // mantenendo l'aspect ratio originale del video (non quello del frame 640x480)
    
    // Per scalare correttamente, dobbiamo:
    // 1. Capire come il frame 640x480 si relaziona al video originale
    // 2. Capire come il video originale si relaziona al video renderizzato
    
    // Il frame 640x480 è una versione ridimensionata/stirata del video originale
    // Quindi le coordinate sono relative a quel frame stirato
    
    // Scaliamo direttamente dalle dimensioni 640x480 alle dimensioni renderizzate
    // Questo funziona perché object-fit: cover riempie il contenitore con il video originale
    // e le coordinate sono relative al frame 640x480 che è una versione del video originale
    const scaleX = renderedWidth / captureWidth;
    const scaleY = renderedHeight / captureHeight;
    
    // Offset per centrare il video (se viene tagliato da object-fit: cover)
    // Quando object-fit: cover taglia il video, parte del video è fuori dal contenitore
    // Le coordinate devono essere spostate per compensare questo taglio
    // Se il video è più largo del contenitore, viene tagliato ai lati -> offsetX negativo
    // Se il video è più alto del contenitore, viene tagliato sopra/sotto -> offsetY negativo
    const offsetX = (renderedWidth - containerWidth) / 2;
    const offsetY = (renderedHeight - containerHeight) / 2;
    
    return {
      scaleX,
      scaleY,
      offsetX: -offsetX, // Negativo perché le coordinate devono essere spostate a sinistra
      offsetY: -offsetY   // Negativo perché le coordinate devono essere spostate in alto
    };
  }, [isCameraReady, videoDimensions]); // Ricalcola quando la camera è pronta o le dimensioni cambiano

  // Handler fullscreen
  const requestFullscreen = () => {
    const el = document.documentElement;
    if (el.requestFullscreen) {
      el.requestFullscreen().catch(() => {});
    } else if (el.webkitRequestFullscreen) {
      el.webkitRequestFullscreen();
    }
    setIsFullscreen(true);
  };

  // Check database status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        console.log('Verifica presenza utente User nel database...');
        const response = await fetch(`${API_BASE_URL}/api/status`);
        if (response.ok) {
          const data = await response.json();
          console.log('Risposta API status:', data);
          
          // Assicurati che has_patient sia un booleano
          const hasUser = Boolean(data.has_patient === true);
          console.log(`Utente User trovato: ${hasUser} (valore originale: ${data.has_patient}, tipo: ${typeof data.has_patient})`);
          
          setHasPatient(hasUser);
        } else {
          const errorText = await response.text();
          console.error('Errore nel controllo stato database:', response.status, errorText);
          setHasPatient(false); // Default a false per mostrare setup
        }
      } catch (error) {
        console.error('Errore di connessione:', error);
        setHasPatient(false); // Default a false per mostrare setup
      } finally {
        setIsCheckingStatus(false);
      }
    };

    checkStatus();
  }, []);

  // Handler per completamento setup
  const handleSetupComplete = () => {
    setHasPatient(true);
    // Ricarica la pagina per aggiornare tutto
    window.location.reload();
  };

  // Handler per successo aggiunta persona
  const handleAddPersonSuccess = () => {
    // Ricarica la pagina per aggiornare il database
    window.location.reload();
  };

  // Se stiamo controllando lo stato, mostra loading
  if (isCheckingStatus || hasPatient === null) {
    return (
      <div className="App">
        <div style={{
          position: 'fixed', inset: 0, background: '#000', zIndex: 100,
          display: 'flex', flexDirection: 'column', alignItems: 'center', 
          justifyContent: 'center', color: '#00ff88'
        }}>
          <div className="spinner" style={{
            width: 50, height: 50, border: '3px solid #333', 
            borderTopColor: '#00ff88', borderRadius: '50%',
            animation: 'spin 1s linear infinite', marginBottom: 20
          }} />
          <div>Controllo configurazione...</div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      </div>
    );
  }

  // Se non c'è paziente (hasPatient è esplicitamente false), mostra setup wizard
  // IMPORTANTE: mostra SetupWizard SOLO se hasPatient è false, non se è null o true
  if (hasPatient === false) {
    console.log('Nessun utente User trovato nel database. Mostro SetupWizard.');
    return (
      <div className="App" style={{ overflow: 'auto', background: 'hsl(var(--background))' }}>
        <SetupWizard onComplete={handleSetupComplete} />
      </div>
    );
  }

  // Se hasPatient è true, NON mostrare SetupWizard
  if (hasPatient === true) {
    console.log('Utente User trovato nel database. Mostro vista principale.');
  }

  // Vista principale con camera (solo se c'è paziente)
  return (
    <div className="App">
      {/* Loading Screen */}
      {!isCameraReady && (
        <div style={{
          position: 'fixed', inset: 0, background: '#000', zIndex: 100,
          display: 'flex', flexDirection: 'column', alignItems: 'center', 
          justifyContent: 'center', color: '#00ff88'
        }}>
          <div className="spinner" style={{
            width: 50, height: 50, border: '3px solid #333', 
            borderTopColor: '#00ff88', borderRadius: '50%',
            animation: 'spin 1s linear infinite', marginBottom: 20
          }} />
          <div>Inizializzazione Camera...</div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      <div
        className="video-container"
        style={{ position: 'relative' }}
        onClick={() => !isFullscreen && requestFullscreen()}
      >
        {/* Beta Banner */}
        <BetaBanner />

        {/* Status Overlay */}
        <StatusOverlay 
          connectionStatus={connectionStatus}
          framesSent={framesSent}
          facesCount={faces.length}
          latency={latency}
          avgLatency={avgLatency}
        />

        {/* Webcam View */}
        <WebcamView
          webcamRef={webcamRef}
          isFrontCamera={isFrontCamera}
          onCameraReady={() => setIsCameraReady(true)}
          isFullscreen={isFullscreen}
          onRequestFullscreen={requestFullscreen}
        />

        {/* Camera Toggle Button */}
        <CameraToggle
          isFrontCamera={isFrontCamera}
          onToggle={() => setIsFrontCamera(!isFrontCamera)}
        />

        {/* Face Boxes */}
        {faces.map((face, index) => (
          <FaceBox
            key={face.id || index}
            face={face}
            scaleX={scaleX}
            scaleY={scaleY}
            offsetX={offsetX}
            offsetY={offsetY}
            index={index}
          />
        ))}

        {/* Pulsante Aggiungi Volto */}
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          zIndex: 30
        }}>
          <Button
            onClick={() => setShowAddPersonDialog(true)}
            variant="secondary"
            size="sm"
            className="flex items-center gap-2"
          >
            <UserPlus className="h-4 w-4" />
            Aggiungi Volto
          </Button>
        </div>
      </div>

      {/* Dialog Aggiungi Persona */}
      <AddPersonDialog
        open={showAddPersonDialog}
        onOpenChange={setShowAddPersonDialog}
        onSuccess={handleAddPersonSuccess}
      />

      {/* Debug Info - Rimuovere dopo il debug */}
      <DebugInfo />
    </div>
  );
}

export default App;
