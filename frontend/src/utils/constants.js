// Costanti configurabili per l'applicazione

// WebSocket
export const getWebSocketUrl = () => {
  // Usa variabili d'ambiente se disponibili, altrimenti inferisci dal browser
  const protocol = process.env.REACT_APP_WS_PROTOCOL || 
                   (window.location.protocol === 'https:' ? 'wss' : 'ws');
  
  const host = process.env.REACT_APP_WS_HOST || window.location.hostname;
  const port = process.env.REACT_APP_WS_PORT || 8000;
  
  return `${protocol}://${host}:${port}/ws`;
};

// API URL
export const getApiUrl = () => {
  // Se REACT_APP_API_URL è definito, usalo direttamente
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Altrimenti costruisci l'URL usando le stesse variabili del WebSocket
  const protocol = process.env.REACT_APP_WS_PROTOCOL === 'wss' ? 'https' : 'http';
  const host = process.env.REACT_APP_WS_HOST || window.location.hostname;
  const port = process.env.REACT_APP_WS_PORT || 8000;
  
  return `${protocol}://${host}:${port}`;
};

// Intervalli e timing
export const MIN_FRAME_INTERVAL = 15; // ms (~13 FPS - bilanciamento ottimale tra fluidità e performance)
export const RECONNECT_BASE_DELAY = 3000; // ms
export const RECONNECT_MAX_DELAY = 15000; // ms

// Risoluzione video
export const VIDEO_CONSTRAINTS = {
  width: { ideal: 1280 },
  height: { ideal: 720 }
};

// Dimensioni frame per l'invio (ridotte per ottimizzare banda)
export const CAPTURE_WIDTH = 640;
export const CAPTURE_HEIGHT = 480;
export const JPEG_QUALITY = 0.7;

