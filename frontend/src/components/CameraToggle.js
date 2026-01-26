import React from 'react';

/**
 * Componente bottone per cambiare camera (front/back)
 */
const CameraToggle = ({ isFrontCamera, onToggle }) => {
  return (
    <div className="camera-toggle-wrapper">
      <button
        className="glass-button"
        onClick={(e) => {
          e.stopPropagation(); // Evita che il click sul bottone attivi il fullscreen
          onToggle();
        }}
      >
        <span className="material-symbols-outlined">switch_camera</span>
      </button>
    </div>
  );
};

export default React.memo(CameraToggle);






