import { useRef, useEffect } from 'react';
import { captureAndSend } from '../utils/videoCapture';
import { MIN_FRAME_INTERVAL } from '../utils/constants';

/**
 * Hook per gestire la cattura e l'invio dei frame via WebSocket
 * Usa requestAnimationFrame per sincronizzazione ottimale con il browser
 * @param {Object} webcamRef - Ref al componente Webcam
 * @param {Object} ws - Ref al WebSocket
 * @param {Object} isProcessing - Ref per tracking dello stato di processamento
 * @param {Function} onFrameSent - Callback chiamata quando viene inviato un frame
 * @returns {Object} { captureCanvasRef }
 */
export const useWebcam = (webcamRef, ws, isProcessing, onFrameSent) => {
  const captureCanvasRef = useRef(null);
  const lastSendTimeRef = useRef(0);

  useEffect(() => {
    let frameId;

    const loop = () => {
      const now = performance.now();
      
      // Controllo throttling e disponibilità
      if (
        now - lastSendTimeRef.current >= MIN_FRAME_INTERVAL &&
        webcamRef.current?.video.readyState === 4 &&
        ws.current?.readyState === WebSocket.OPEN &&
        !isProcessing.current
      ) {
        isProcessing.current = true;
        lastSendTimeRef.current = now;
        
        const video = webcamRef.current.video;
        const sent = captureAndSend(video, ws.current, captureCanvasRef.current);
        
        // Marca timestamp invio per calcolo latenza
        if (sent && onFrameSent) {
          onFrameSent();
        }
      }
      
      frameId = requestAnimationFrame(loop);
    };

    frameId = requestAnimationFrame(loop);
    
    return () => {
      if (frameId) {
        cancelAnimationFrame(frameId);
      }
    };
  }, [onFrameSent]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    captureCanvasRef
  };
};

