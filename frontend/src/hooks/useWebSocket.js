import { useRef, useState, useEffect } from 'react';
import { getWebSocketUrl, RECONNECT_BASE_DELAY, RECONNECT_MAX_DELAY } from '../utils/constants';

/**
 * Hook per gestire la connessione WebSocket con riconnessione automatica
 * @param {Function} onMessage - Callback chiamata quando arriva un messaggio
 * @returns {Object} { ws, connectionStatus, isProcessing }
 */
export const useWebSocket = (onMessage) => {
  const ws = useRef(null);
  const reconnectTimerRef = useRef(null);
  const isProcessing = useRef(false);
  
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const scheduleReconnect = () => {
    if (reconnectTimerRef.current) return;

    setReconnectAttempts((prev) => {
      const attempt = prev + 1;
      const delay = Math.min(RECONNECT_BASE_DELAY * attempt, RECONNECT_MAX_DELAY);
      
      reconnectTimerRef.current = setTimeout(() => {
        reconnectTimerRef.current = null;
        initWebSocket();
      }, delay);
      
      return attempt;
    });
  };

  const initWebSocket = () => {
    try {
      const wsUrl = getWebSocketUrl();
      console.log("Tentativo di connessione WebSocket a:", wsUrl);
      const socket = new WebSocket(wsUrl);
      ws.current = socket;

      socket.onopen = () => {
        console.log("WS Connesso con successo a:", wsUrl);
        setConnectionStatus("connected");
        setReconnectAttempts(0);
        if (reconnectTimerRef.current) {
          clearTimeout(reconnectTimerRef.current);
          reconnectTimerRef.current = null;
        }
      };

      socket.onclose = (event) => {
        console.log("WS Disconnesso. Code:", event.code, "Reason:", event.reason);
        setConnectionStatus("disconnected");
        scheduleReconnect();
      };

      socket.onerror = (err) => {
        console.error("Errore WebSocket:", err);
        setConnectionStatus("error");
        scheduleReconnect();
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        isProcessing.current = false;
        
        if (onMessage) {
          onMessage(data);
        }
      };
    } catch (e) {
      console.error("Errore nell'inizializzazione WebSocket:", e);
      setConnectionStatus("error");
      scheduleReconnect();
    }
  };

  useEffect(() => {
    initWebSocket();
    
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    ws,
    connectionStatus,
    isProcessing
  };
};






