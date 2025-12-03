import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import './App.css'; // Assicurati di importare il CSS

function App() {
  const webcamRef = useRef(null);
  const ws = useRef(null);
  const reconnectTimerRef = useRef(null);
  
  const [faces, setFaces] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const [framesSent, setFramesSent] = useState(0);
  const [isFrontCamera, setIsFrontCamera] = useState(true);
  const [, setReconnectAttempts] = useState(0);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Forza transform per evitare specchiamento indesiderato
  useEffect(() => {
    const applyVideoTransform = () => {
      // Nota: ora usiamo la classe .webcam-video definita nel CSS
      const video = document.querySelector('.webcam-video');
      if (video) {
        // Su mobile "user" è spesso specchiato di default, "environment" no.
        // Qui forziamo scaleX(1) per annullare mirror se la libreria lo applica.
        video.style.transform = 'scaleX(1)'; 
      }
    };
    const interval = setInterval(applyVideoTransform, 500);
    window.addEventListener('orientationchange', applyVideoTransform);
    return () => {
      clearInterval(interval);
      window.removeEventListener('orientationchange', applyVideoTransform);
    };
  }, []);

  // --- LOGICA WEBSOCKET (Invariata) ---
  const getWebSocketUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname;
    const port = 8000; 
    return `${protocol}://${host}:${port}/ws`;
  };

  const scheduleReconnect = () => {
    if (reconnectTimerRef.current) return;
    const baseDelay = 3000;
    const maxDelay = 15000;

    setReconnectAttempts((prev) => {
      const attempt = prev + 1;
      const delay = Math.min(baseDelay * attempt, maxDelay);
      reconnectTimerRef.current = setTimeout(() => {
        reconnectTimerRef.current = null;
        initWebSocket();
      }, delay);
      return attempt;
    });
  };

  const initWebSocket = () => {
    try {
      const socket = new WebSocket(getWebSocketUrl());
      ws.current = socket;

      socket.onopen = () => {
        console.log("WS Connesso");
        setConnectionStatus("connected");
        setReconnectAttempts(0);
        if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      };

      socket.onclose = () => {
        setConnectionStatus("disconnected");
        scheduleReconnect();
      };

      socket.onerror = (err) => {
        setConnectionStatus("error");
        scheduleReconnect();
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setFaces(data.faces);
      };
    } catch (e) {
      setConnectionStatus("error");
      scheduleReconnect();
    }
  };

  useEffect(() => {
    initWebSocket();
    return () => {
      if (ws.current) ws.current.close();
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Invio Frame
  useEffect(() => {
    const interval = setInterval(() => {
      if (
        webcamRef.current &&
        webcamRef.current.video.readyState === 4 &&
        ws.current.readyState === WebSocket.OPEN
      ) {
        captureAndSend();
      }
    }, 100); 
    return () => clearInterval(interval);
  }, []);

  const captureAndSend = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      ws.current.send(imageSrc); 
      setFramesSent((prev) => prev + 1);
    }
  };

  const requestFullscreen = () => {
    const el = document.documentElement;
    // Tenta fullscreen standard
    if (el.requestFullscreen) el.requestFullscreen().catch(() => {});
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    setIsFullscreen(true);
  };

  // Video Constraints: Usa aspect ratio verticale per mobile se vuoi riempire meglio,
  // ma object-fit: cover nel CSS farà il grosso del lavoro.
  const videoConstraints = {
    facingMode: isFrontCamera ? "user" : { exact: "environment" },
    width: { ideal: 1920 }, // Alziamo la risoluzione richiesta
    height: { ideal: 1080 }
  };

  return (
    <div className="App">
      {/* Loading Screen */}
      {!isCameraReady && (
        <div style={{
            position: 'fixed', inset: 0, background: '#000', zIndex: 100,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#00ff88'
          }}>
          <div className="spinner" style={{
              width: 50, height: 50, border: '3px solid #333', borderTopColor: '#00ff88', borderRadius: '50%',
              animation: 'spin 1s linear infinite', marginBottom: 20
          }}/>
          <div>Inizializzazione Camera...</div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      <div className="video-container" onClick={() => !isFullscreen && requestFullscreen()}>
        
        {/* Debug Overlay */}
        <div className="status-overlay">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>lan</span>
            <span>SYSTEM_STATUS</span>
          </div>
          <div>WS: <span style={{color: connectionStatus==='connected'?'#00ff88':'#ff4444'}}>{connectionStatus}</span></div>
          <div>FRAMES: {framesSent}</div>
          <div>TARGETS: {faces.length}</div>
        </div>
        
        {/* Layer 1: Webcam */}
        {/* Nota l'attributo className="webcam-video" che si collega al CSS */}
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          mirrored={false} 
          className="webcam-video" 
          onUserMedia={() => setIsCameraReady(true)}
          key={isFrontCamera ? "front" : "back"}
        />

        {/* Layer 2: Bottone Glassmorphism Custom */}
        <div className="camera-toggle-wrapper">
          <button 
            className="glass-button"
            onClick={(e) => {
              e.stopPropagation(); // Evita che il click sul bottone attivi il fullscreen
              setIsFrontCamera(!isFrontCamera);
            }}
          >
            <span className="material-symbols-outlined">switch_camera</span>
          </button>
        </div>

        {/* Layer 3: Riquadri Volti (CSS migliorato) */}
        {faces.map((face, index) => {
          // Calcolo dinamico della posizione per adattarsi al video 'cover'
          // Nota: Questo calcolo presuppone che il backend mandi coordinate relative al frame video originale.
          // Se il video viene tagliato dal CSS object-fit: cover, le coordinate potrebbero sfasare leggermente 
          // a seconda di come il browser centra il video. 
          // Per una precisione millimetrica servirebbe calcolare l'aspect ratio, ma per ora usiamo % o px diretti.
          
          const nameNormalized = (face.name || "").toString().trim().toLowerCase();
          const isUnknown = !nameNormalized || nameNormalized.includes("sconosciuto") || nameNormalized === "unknown";

          return (
            <div
              key={index}
              className={`face-box ${isUnknown ? 'unknown' : ''}`}
              style={{
                top: face.top,
                left: face.left,
                width: face.right - face.left,
                height: face.bottom - face.top,
              }}
            >
              <div className="face-label">
                {face.name || "UNKNOWN"}
              </div>
            </div>
          );
        })}

      </div>
    </div>
  );
}

export default App;