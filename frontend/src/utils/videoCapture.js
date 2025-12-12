// Funzioni per cattura e compressione frame video
import { CAPTURE_WIDTH, CAPTURE_HEIGHT, JPEG_QUALITY } from './constants';

/**
 * Cattura un frame dal video e lo ridimensiona a 640x480 per ottimizzare banda
 * @param {HTMLVideoElement} video - Elemento video da cui catturare
 * @param {HTMLCanvasElement} canvas - Canvas riutilizzabile (opzionale)
 * @returns {HTMLCanvasElement|null} Canvas con il frame catturato
 */
export const captureFrame = (video, canvas = null) => {
  if (!video || !video.videoWidth || !video.videoHeight) {
    return null;
  }

  // Crea o riutilizza il canvas
  if (!canvas) {
    canvas = document.createElement('canvas');
  }

  // Imposta dimensioni ridotte (ottimizzazione prestazioni)
  if (canvas.width !== CAPTURE_WIDTH || canvas.height !== CAPTURE_HEIGHT) {
    canvas.width = CAPTURE_WIDTH;
    canvas.height = CAPTURE_HEIGHT;
  }

  const ctx = canvas.getContext('2d');
  if (!ctx) return null;

  // Disegna il frame ridimensionato
  ctx.drawImage(video, 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT);

  return canvas;
};

/**
 * Converte un canvas in BLOB JPEG compresso
 * @param {HTMLCanvasElement} canvas - Canvas da convertire
 * @param {Function} callback - Callback chiamata con il blob
 */
export const canvasToBlob = (canvas, callback) => {
  canvas.toBlob(callback, 'image/jpeg', JPEG_QUALITY);
};

/**
 * Cattura e invia un frame via WebSocket
 * @param {HTMLVideoElement} video - Elemento video
 * @param {WebSocket} ws - WebSocket connection
 * @param {HTMLCanvasElement} canvasRef - Canvas riutilizzabile
 * @returns {boolean} True se l'invio è stato avviato
 */
export const captureAndSend = (video, ws, canvasRef) => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    return false;
  }

  const canvas = captureFrame(video, canvasRef);
  if (!canvas) return false;

  canvasToBlob(canvas, (blob) => {
    if (blob && ws.readyState === WebSocket.OPEN) {
      ws.send(blob);
    }
  });

  return true;
};

