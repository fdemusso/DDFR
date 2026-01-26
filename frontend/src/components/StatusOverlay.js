import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Activity, Wifi, Video, Users, Gauge } from 'lucide-react';

/**
 * Componente per visualizzare informazioni di debug/stato
 */
const StatusOverlay = ({ connectionStatus, framesSent, facesCount, latency, avgLatency }) => {
  // Variante badge per latenza basata su performance
  const getLatencyVariant = (lat) => {
    if (lat < 50) return 'success'; // Verde - Ottimo
    if (lat < 100) return 'success'; // Verde - Buono
    if (lat < 150) return 'warning'; // Giallo - Accettabile
    if (lat < 250) return 'warning'; // Giallo - Lento
    return 'error'; // Rosso - Molto lento
  };

  const isConnected = connectionStatus === 'connected';

  return (
    <Card className="absolute top-2 left-2 z-10 bg-background/95 backdrop-blur-sm border shadow-lg min-w-[200px]">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <CardTitle className="text-sm">System Status</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* WebSocket Status */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Wifi className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">WebSocket</span>
          </div>
          <Badge 
            variant={isConnected ? 'success' : 'error'}
            className="text-xs ml-auto"
          >
            {connectionStatus}
          </Badge>
        </div>

        <Separator />

        {/* Frames Sent */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Video className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">Frames</span>
          </div>
          <Badge variant="secondary" className="font-mono text-xs">
            {framesSent}
          </Badge>
        </div>

        {/* Targets Detected */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">Targets</span>
          </div>
          <Badge variant="secondary" className="font-mono text-xs">
            {facesCount}
          </Badge>
        </div>

        <Separator />

        {/* Latency */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gauge className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Latency</span>
            </div>
            <Badge 
              variant={getLatencyVariant(latency)}
              className="font-mono text-xs"
            >
              {latency}ms
            </Badge>
          </div>
          {avgLatency > 0 && (
            <div className="flex justify-end">
              <span className="text-[10px] text-muted-foreground">
                avg: {avgLatency}ms
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(StatusOverlay);

