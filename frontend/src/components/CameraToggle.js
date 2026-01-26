import React from 'react';
import { Button } from './ui/button';
import { SwitchCamera } from 'lucide-react';

/**
 * Componente bottone per cambiare camera (front/back)
 */
const CameraToggle = ({ isFrontCamera, onToggle }) => {
  return (
    <div 
      className="absolute bottom-[calc(40px+env(safe-area-inset-bottom))] left-1/2 -translate-x-1/2 z-50"
      onClick={(e) => e.stopPropagation()} // Evita che il click attivi il fullscreen
    >
      <Button
        variant="secondary"
        size="icon"
        className="h-14 w-14 rounded-full bg-background/80 backdrop-blur-sm border shadow-lg hover:bg-background/90 transition-all"
        onClick={(e) => {
          e.stopPropagation(); // Evita che il click sul bottone attivi il fullscreen
          onToggle();
        }}
        aria-label={isFrontCamera ? 'Passa alla fotocamera posteriore' : 'Passa alla fotocamera anteriore'}
      >
        <SwitchCamera className="h-6 w-6" />
      </Button>
    </div>
  );
};

export default React.memo(CameraToggle);






