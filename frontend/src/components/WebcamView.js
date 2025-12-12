import React, { useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import { VIDEO_CONSTRAINTS } from '../utils/constants';

/**
 * Componente wrapper per la Webcam con gestione fullscreen
 */
const WebcamView = ({ webcamRef, isFrontCamera, onCameraReady, isFullscreen, onRequestFullscreen }) => {
  const [videoConstraints, setVideoConstraints] = useState({
    ...VIDEO_CONSTRAINTS,
    facingMode: isFrontCamera ? "user" : { exact: "environment" }
  });

  // Aggiorna constraints quando cambia la camera
  useEffect(() => {
    setVideoConstraints({
      ...VIDEO_CONSTRAINTS,
      facingMode: isFrontCamera ? "user" : { exact: "environment" }
    });
  }, [isFrontCamera]);

  // Forza transform per evitare specchiamento indesiderato
  useEffect(() => {
    const applyVideoTransform = () => {
      const video = document.querySelector('.webcam-video');
      if (video) {
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

  return (
    <Webcam
      audio={false}
      ref={webcamRef}
      screenshotFormat="image/jpeg"
      videoConstraints={videoConstraints}
      mirrored={false}
      className="webcam-video"
      onUserMedia={onCameraReady}
      key={isFrontCamera ? "front" : "back"}
    />
  );
};

export default React.memo(WebcamView);

