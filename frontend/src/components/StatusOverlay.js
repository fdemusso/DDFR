import React from 'react';

/**
 * Componente per visualizzare informazioni di debug/stato
 */
const StatusOverlay = ({ connectionStatus, framesSent, facesCount, latency, avgLatency }) => {
  // Colore latenza basato su performance
  const getLatencyColor = (lat) => {
    if (lat < 50) return '#00ff88'; // Verde - Ottimo
    if (lat < 100) return '#88ff00'; // Verde chiaro - Buono
    if (lat < 150) return '#ffff00'; // Giallo - Accettabile
    if (lat < 250) return '#ff8800'; // Arancione - Lento
    return '#ff4444'; // Rosso - Molto lento
  };

  return (
    <div className="status-overlay">
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>lan</span>
        <span>SYSTEM_STATUS</span>
      </div>
      <div>
        WS: <span style={{ color: connectionStatus === 'connected' ? '#00ff88' : '#ff4444' }}>
          {connectionStatus}
        </span>
      </div>
      <div>FRAMES: {framesSent}</div>
      <div>TARGETS: {facesCount}</div>
      <div>
        LATENCY: <span style={{ color: getLatencyColor(latency) }}>
          {latency}ms
        </span>
        {avgLatency > 0 && (
          <span style={{ opacity: 0.7, fontSize: 10 }}> (avg: {avgLatency}ms)</span>
        )}
      </div>
    </div>
  );
};

export default React.memo(StatusOverlay);

