import React from 'react';

/**
 * Componente per debug della connessione WebSocket
 */
const DebugInfo = () => {
  const wsUrl = (() => {
    const protocol = process.env.REACT_APP_WS_PROTOCOL || 
                     (window.location.protocol === 'https:' ? 'wss' : 'ws');
    const host = process.env.REACT_APP_WS_HOST || window.location.hostname;
    const port = process.env.REACT_APP_WS_PORT || 8000;
    return `${protocol}://${host}:${port}/ws`;
  })();

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      left: 20,
      right: 20,
      background: 'rgba(0,0,0,0.9)',
      color: '#00ff88',
      padding: 15,
      borderRadius: 8,
      fontFamily: 'monospace',
      fontSize: 12,
      zIndex: 1000,
      maxWidth: 600
    }}>
      <h3 style={{ margin: '0 0 10px 0', color: '#fff' }}>🔍 DEBUG INFO</h3>
      <div><strong>WebSocket URL:</strong> {wsUrl}</div>
      <div><strong>REACT_APP_WS_PROTOCOL:</strong> {process.env.REACT_APP_WS_PROTOCOL || '(not set)'}</div>
      <div><strong>REACT_APP_WS_HOST:</strong> {process.env.REACT_APP_WS_HOST || '(not set)'}</div>
      <div><strong>REACT_APP_WS_PORT:</strong> {process.env.REACT_APP_WS_PORT || '(not set)'}</div>
      <div><strong>window.location.protocol:</strong> {window.location.protocol}</div>
      <div><strong>window.location.hostname:</strong> {window.location.hostname}</div>
      <div><strong>window.location.port:</strong> {window.location.port}</div>
      <div style={{ marginTop: 10, padding: 10, background: 'rgba(255,255,255,0.1)', borderRadius: 4 }}>
        <strong>Apri la Console (F12) per vedere i log di connessione WebSocket</strong>
      </div>
    </div>
  );
};

export default DebugInfo;




