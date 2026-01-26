import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import { Button } from './ui/button';
import { Terminal, ExternalLink, Info, ChevronDown, ChevronUp } from 'lucide-react';

/**
 * Componente per debug della connessione WebSocket
 */
const DebugInfo = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const wsUrl = (() => {
    const protocol = process.env.REACT_APP_WS_PROTOCOL || 
                     (window.location.protocol === 'https:' ? 'wss' : 'ws');
    const host = process.env.REACT_APP_WS_HOST || window.location.hostname;
    const port = process.env.REACT_APP_WS_PORT || 8000;
    return `${protocol}://${host}:${port}/ws`;
  })();

  const envVars = [
    { label: 'REACT_APP_WS_PROTOCOL', value: process.env.REACT_APP_WS_PROTOCOL || '(not set)' },
    { label: 'REACT_APP_WS_HOST', value: process.env.REACT_APP_WS_HOST || '(not set)' },
    { label: 'REACT_APP_WS_PORT', value: process.env.REACT_APP_WS_PORT || '(not set)' },
  ];

  const locationVars = [
    { label: 'Protocol', value: window.location.protocol },
    { label: 'Hostname', value: window.location.hostname },
    { label: 'Port', value: window.location.port || '(default)' },
  ];

  return (
    <Card className={`fixed bottom-5 left-5 right-5 z-[1000] max-w-[600px] bg-background/95 backdrop-blur-sm border shadow-lg transition-all duration-300 ${isExpanded ? '' : 'max-h-[80px] overflow-hidden'}`}>
      <CardHeader className={`pb-3 ${!isExpanded ? 'py-2' : ''}`}>
        <div className={`flex items-center ${!isExpanded ? 'justify-center gap-3' : 'justify-between'}`}>
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-primary" />
            <CardTitle className="text-base">Debug Info</CardTitle>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-label={isExpanded ? 'Riduci' : 'Espandi'}
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
        {isExpanded && (
          <CardDescription className="text-xs text-center">
            Informazioni di connessione WebSocket
          </CardDescription>
        )}
      </CardHeader>
      {isExpanded && (
        <CardContent className="space-y-4">
          {/* WebSocket URL */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">WebSocket URL</span>
              <Badge variant="outline" className="font-mono text-xs">
                <ExternalLink className="h-3 w-3 mr-1" />
                {wsUrl}
              </Badge>
            </div>
          </div>

          <Separator />

          {/* Environment Variables */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
              Variabili d'Ambiente
            </h4>
            <div className="space-y-1.5">
              {envVars.map((env, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="font-mono text-muted-foreground">{env.label}:</span>
                  <Badge 
                    variant={env.value === '(not set)' ? "outline" : "secondary"}
                    className="font-mono"
                  >
                    {env.value}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Window Location */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
              Window Location
            </h4>
            <div className="space-y-1.5">
              {locationVars.map((loc, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="font-mono text-muted-foreground">{loc.label}:</span>
                  <Badge variant="outline" className="font-mono">
                    {loc.value}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Alert */}
          <Alert className="bg-muted/50">
            <div className="flex items-center justify-center gap-2">
              <Info className="h-4 w-4" />
              <AlertDescription className="text-xs text-center">
                Apri la Console (F12) per vedere i log di connessione WebSocket
              </AlertDescription>
            </div>
          </Alert>
        </CardContent>
      )}
    </Card>
  );
};

export default DebugInfo;






