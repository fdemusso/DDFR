import { useState, useRef, useCallback } from 'react';

/**
 * Hook per tracciare la latenza tra invio frame e ricezione risposta
 * @returns {Object} { latency, avgLatency, markSent, markReceived }
 */
export const useLatency = () => {
  const [latency, setLatency] = useState(0); // Latenza corrente
  const [avgLatency, setAvgLatency] = useState(0); // Latenza media
  const sentTimeRef = useRef(null);
  const latencyHistoryRef = useRef([]);
  const maxHistorySize = 10; // Media sulle ultime 10 misurazioni

  // Chiamata quando viene inviato un frame
  const markSent = useCallback(() => {
    sentTimeRef.current = performance.now();
  }, []);

  // Chiamata quando viene ricevuta una risposta
  const markReceived = useCallback(() => {
    if (sentTimeRef.current === null) return;

    const currentLatency = performance.now() - sentTimeRef.current;
    setLatency(Math.round(currentLatency));

    // Aggiorna storia per calcolo media
    latencyHistoryRef.current.push(currentLatency);
    if (latencyHistoryRef.current.length > maxHistorySize) {
      latencyHistoryRef.current.shift(); // Rimuovi il più vecchio
    }

    // Calcola media
    const sum = latencyHistoryRef.current.reduce((a, b) => a + b, 0);
    const avg = sum / latencyHistoryRef.current.length;
    setAvgLatency(Math.round(avg));

    sentTimeRef.current = null;
  }, []);

  return {
    latency,
    avgLatency,
    markSent,
    markReceived
  };
};



