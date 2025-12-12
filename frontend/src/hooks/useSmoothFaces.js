import { useState, useRef, useEffect } from 'react';

/**
 * Hook per smoothing delle coordinate dei volti
 * Riduce il tremolio applicando una soglia minima di movimento
 * @param {Array} rawFaces - Array dei volti da smoothare
 * @param {number} threshold - Soglia minima di movimento in pixel (default: 8)
 * @returns {Array} Array dei volti con coordinate smoothed
 */
export const useSmoothFaces = (rawFaces, threshold = 8) => {
  const [smoothedFaces, setSmoothedFaces] = useState([]);
  const previousFacesRef = useRef({});

  useEffect(() => {
    if (!rawFaces || rawFaces.length === 0) {
      setSmoothedFaces([]);
      previousFacesRef.current = {};
      return;
    }

    const newSmoothedFaces = rawFaces.map((face) => {
      const faceId = face.id || `${face.name}_${face.top}_${face.left}`;
      const prevFace = previousFacesRef.current[faceId];

      if (!prevFace) {
        // Nuovo volto, nessuno smoothing
        previousFacesRef.current[faceId] = face;
        return face;
      }

      // Calcola la distanza dal frame precedente
      const deltaTop = Math.abs(face.top - prevFace.top);
      const deltaLeft = Math.abs(face.left - prevFace.left);
      const deltaRight = Math.abs(face.right - prevFace.right);
      const deltaBottom = Math.abs(face.bottom - prevFace.bottom);

      // Se il movimento è sotto la soglia, usa le coordinate precedenti
      const shouldUpdate = 
        deltaTop > threshold ||
        deltaLeft > threshold ||
        deltaRight > threshold ||
        deltaBottom > threshold;

      if (shouldUpdate) {
        // Applica smoothing leggero con interpolazione (85% nuovo, 15% vecchio)
        // Meno interpolazione = movimento più diretto e naturale
        const smoothedFace = {
          ...face,
          top: prevFace.top * 0.15 + face.top * 0.85,
          left: prevFace.left * 0.15 + face.left * 0.85,
          right: prevFace.right * 0.15 + face.right * 0.85,
          bottom: prevFace.bottom * 0.15 + face.bottom * 0.85,
        };
        previousFacesRef.current[faceId] = smoothedFace;
        return smoothedFace;
      } else {
        // Movimento troppo piccolo, mantieni posizione precedente
        return prevFace;
      }
    });

    setSmoothedFaces(newSmoothedFaces);

    // Cleanup: rimuovi volti che non sono più presenti
    const currentIds = new Set(rawFaces.map(f => f.id || `${f.name}_${f.top}_${f.left}`));
    Object.keys(previousFacesRef.current).forEach(id => {
      if (!currentIds.has(id)) {
        delete previousFacesRef.current[id];
      }
    });
  }, [rawFaces, threshold]);

  return smoothedFaces;
};

