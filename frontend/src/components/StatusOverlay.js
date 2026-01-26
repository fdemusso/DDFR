import React from 'react';
import { Card, CardContent } from './ui/card';

/**
 * Componente per visualizzare informazioni di debug/stato
 */
const StatusOverlay = ({ connectionStatus, framesSent, facesCount, latency, avgLatency }) => {
  // Colore latenza basato su performance
  const getLatencyColor = (lat) => {
    if (lat < 50) return 'text-green-500'; // Verde - Ottimo
    if (lat < 100) return 'text-green-400'; // Verde chiaro - Buono
    if (lat < 150) return 'text-yellow-500'; // Giallo - Accettabile
    if (lat < 250) return 'text-orange-500'; // Arancione - Lento
    return 'text-red-500'; // Rosso - Molto lento
  };

  return (
    <Card className="absolute top-2 left-2 z-10 bg-black/60 border-border/50">
      <CardContent className="p-2 text-xs font-mono text-green-500">
        <div className="flex items-center gap-2 mb-1">
          <span className="material-symbols-outlined text-sm">lan</span>
          <span>SYSTEM_STATUS</span>
        </div>
        <div>
          WS: <span className={connectionStatus === 'connected' ? 'text-green-500' : 'text-red-500'}>
            {connectionStatus}
          </span>
        </div>
        <div>FRAMES: {framesSent}</div>
        <div>TARGETS: {facesCount}</div>
        <div>
          LATENCY: <span className={getLatencyColor(latency)}>
            {latency}ms
          </span>
          {avgLatency > 0 && (
            <span className="opacity-70 text-[10px]"> (avg: {avgLatency}ms)</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(StatusOverlay);

