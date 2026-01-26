import React from 'react';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Beaker } from 'lucide-react';

/**
 * Banner per indicare che questa è una versione beta
 */
const BetaBanner = () => {
  return (
    <div className="absolute top-2 left-1/2 -translate-x-1/2 z-40">
      <Alert className="bg-background/90 backdrop-blur-sm border shadow-lg px-3 py-2">
        <div className="flex items-center gap-2">
          <Beaker className="h-4 w-4 text-primary" />
          <AlertDescription className="text-xs font-medium">
            Versione <Badge variant="warning" className="ml-1 text-[10px] px-1.5 py-0">BETA</Badge>
          </AlertDescription>
        </div>
      </Alert>
    </div>
  );
};

export default BetaBanner;
