import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

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
    <Card className="fixed bottom-5 left-5 right-5 z-[1000] max-w-[600px] bg-black/90 border-border/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-white">🔍 DEBUG INFO</CardTitle>
      </CardHeader>
      <CardContent className="text-xs font-mono text-green-500 space-y-1">
        <div><strong>WebSocket URL:</strong> {wsUrl}</div>
        <div><strong>REACT_APP_WS_PROTOCOL:</strong> {process.env.REACT_APP_WS_PROTOCOL || '(not set)'}</div>
        <div><strong>REACT_APP_WS_HOST:</strong> {process.env.REACT_APP_WS_HOST || '(not set)'}</div>
        <div><strong>REACT_APP_WS_PORT:</strong> {process.env.REACT_APP_WS_PORT || '(not set)'}</div>
        <div><strong>window.location.protocol:</strong> {window.location.protocol}</div>
        <div><strong>window.location.hostname:</strong> {window.location.hostname}</div>
        <div><strong>window.location.port:</strong> {window.location.port}</div>
        <div className="mt-2 p-2 bg-white/10 rounded">
          <strong>Apri la Console (F12) per vedere i log di connessione WebSocket</strong>
        </div>
      </CardContent>
    </Card>
  );
};

export default DebugInfo;






