import { useState } from 'react';

/**
 * Hook per gestire lo stato dei volti rilevati
 * @returns {Object} { faces, setFaces, framesSent, setFramesSent }
 */
export const useFaceDetection = () => {
  const [faces, setFaces] = useState([]);
  const [framesSent, setFramesSent] = useState(0);

  return {
    faces,
    setFaces,
    framesSent,
    setFramesSent
  };
};



