import React, { useRef, useState, useMemo, useEffect } from 'react';
import './App.css';

// Custom Hooks
import { useWebSocket } from './hooks/useWebSocket';
import { useWebcam } from './hooks/useWebcam';
import { useFaceDetection } from './hooks/useFaceDetection';
import { useLatency } from './hooks/useLatency';

// Constants
import { CAPTURE_WIDTH, CAPTURE_HEIGHT } from './utils/constants';

// Componenti
import WebcamView from './components/WebcamView';
import FaceBox from './components/FaceBox';
import StatusOverlay from './components/StatusOverlay';
import CameraToggle from './components/CameraToggle';
import DebugInfo from './components/DebugInfo';
import SetupWizard from './components/SetupWizard';
import AddPersonDialog from './components/AddPersonDialog';
import { Button } from './components/ui/button';
import { UserPlus } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
  const { captureCanvasRef } = useWebcam(webcamRef, ws, isProcessing, markSent);

  // Calcolo scale factors con useMemo (ottimizzazione)
  // Le coordinate dal backend sono basate sul frame ridimensionato (CAPTURE_WIDTH x CAPTURE_HEIGHT)
  // quindi dobbiamo scalare da quelle dimensioni alle dimensioni mostrate del video
  const { scaleX, scaleY } = useMemo(() => {
    const videoEl = webcamRef.current?.video;
    if (!videoEl || !videoEl.clientWidth || !videoEl.clientHeight) {
      return { scaleX: 1, scaleY: 1 };
    }
    
    return {
      scaleX: videoEl.clientWidth / CAPTURE_WIDTH,
      scaleY: videoEl.clientHeight / CAPTURE_HEIGHT,
    };
  }, [faces]); // Ricalcola quando cambiano i faces

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
        const response = await fetch(`${API_BASE_URL}/api/status`);
        if (response.ok) {
          const data = await response.json();
          setHasPatient(data.has_patient);
        } else {
          console.error('Errore nel controllo stato database');
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

  // Se non c'è paziente, mostra setup wizard
  if (!hasPatient) {
    return (
      <div className="App">
        <SetupWizard onComplete={handleSetupComplete} />
      </div>
    );
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
