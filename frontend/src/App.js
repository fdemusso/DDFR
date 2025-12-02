import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';

function App() {
  const webcamRef = useRef(null);
  const ws = useRef(null);
  const [faces, setFaces] = useState([]); // dati backend

  // Configurazione Iniziale del WebSocket
  useEffect(() => {
    // Connessione backend
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onopen = () => {
      console.log("Connessione WebSocket aperta!");
    };

    ws.current.onclose = () => {
      console.log("Connessione WebSocket chiusa");
    };

    // Quando Python ci risponde con i dati delle facce...
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // data.faces sarà l'array con le coordinate che Python ha calcolato
      setFaces(data.faces); 
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  // invio dei frame
  useEffect(() => {
    const interval = setInterval(() => {
      // Controlliamo se la webcam è pronta e se il socket è aperto
      if (
        webcamRef.current &&
        webcamRef.current.video.readyState === 4 && // 4 significa "HAVE_ENOUGH_DATA"
        ws.current.readyState === WebSocket.OPEN
      ) {
        captureAndSend();
      }
    }, 100); // 100ms = 10 FPS

    return () => clearInterval(interval);
  }, []);

  const captureAndSend = () => {
    //Estrai lo screenshot in formato Base64 (stringa)
    const imageSrc = webcamRef.current.getScreenshot();
    
    // Invialo al backend
    if (imageSrc) {
      ws.current.send(imageSrc); 
    }
  };

  // Stile per il video e l'overlay
  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user"
  };

  return (
    <div className="App" style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
      
      {/* Contenitore Relativo: serve per sovrapporre i box al video */}
      <div style={{ position: 'relative', width: '640px', height: '480px' }}>
        
        {/* Layer 1: La Webcam */}
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          width={640}
          height={480}
          videoConstraints={videoConstraints}
          style={{ position: 'absolute', top: 0, left: 0 }}
        />

        {/* Layer 2: I Riquadri (Bounding Boxes) */}
        {/* Disegniamo un div per ogni faccia trovata */}
        {faces.map((face, index) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              border: '3px solid #00FF00', // Verde Hacker
              backgroundColor: 'rgba(0, 255, 0, 0.1)', // Leggermente colorato dentro
              
              // Mapping delle coordinate ricevute dal Backend
              top: face.top,
              left: face.left,
              width: face.right - face.left, // Larghezza = Destra - Sinistra
              height: face.bottom - face.top, // Altezza = Fondo - Cima
            }}
          >
            {/* Etichetta col nome (se c'è) */}
            <span style={{ 
                position: 'absolute', 
                top: -25, 
                left: 0, 
                backgroundColor: '#00FF00', 
                color: 'black', 
                padding: '2px 5px', 
                fontWeight: 'bold' 
            }}>
              {face.name || "Sconosciuto"}
            </span>
          </div>
        ))}

      </div>
    </div>
  );
}

export default App;