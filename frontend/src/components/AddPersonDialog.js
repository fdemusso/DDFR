import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from './ui/dialog';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import PhotoUploader from './PhotoUploader';
import PersonForm from './PersonForm';
import { ChevronRight, ChevronLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import { getApiUrl } from '../utils/constants';

const API_BASE_URL = getApiUrl();

const AddPersonDialog = ({ open, onOpenChange, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const totalSteps = 3; // Intro, Foto, Form (no preview per dialog)

  const resetDialog = () => {
    setCurrentStep(1);
    setPhotos([]);
    setError(null);
    setLoading(false);
  };

  const handleClose = () => {
    resetDialog();
    onOpenChange(false);
  };

  const handlePhotosChange = (newPhotos) => {
    setPhotos(newPhotos);
  };

  const handleFormSubmit = async (data) => {
    if (photos.length === 0) {
      setError('Devi caricare almeno una foto');
      setCurrentStep(2);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Prepara FormData
      const formDataToSend = new FormData();
      formDataToSend.append('name', data.name);
      formDataToSend.append('surname', data.surname);
      formDataToSend.append('birthday', data.birthday);
      formDataToSend.append('relationship', data.relationship);
      formDataToSend.append('role', 'guest'); // Sempre GUEST per nuovi volti

      // Aggiungi tutte le foto
      photos.forEach((photo) => {
        formDataToSend.append('photos', photo);
      });

      const response = await fetch(`${API_BASE_URL}/api/person`, {
        method: 'POST',
        body: formDataToSend,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Errore sconosciuto' }));
        throw new Error(errorData.detail || `Errore ${response.status}`);
      }

      const result = await response.json();
      console.log('Persona creata:', result);
      
      // Reset e chiudi
      resetDialog();
      onOpenChange(false);
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      setError(err.message || 'Errore durante il salvataggio della persona');
      console.error('Errore:', err);
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep === 2 && photos.length === 0) {
      setError('Devi caricare almeno una foto per continuare');
      return;
    }
    setError(null);
    setCurrentStep((prev) => Math.min(prev + 1, totalSteps));
  };

  const prevStep = () => {
    setError(null);
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Aggiungi un Nuovo Volto</h3>
            <p className="text-sm text-muted-foreground">
              Aggiungi una nuova persona al sistema di riconoscimento. Carica le foto e inserisci i dati anagrafici.
            </p>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li>Carica o scatta una o più foto del volto</li>
              <li>Inserisci i dati anagrafici</li>
              <li>Conferma e salva</li>
            </ul>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Carica le Foto del Volto</h3>
            <p className="text-sm text-muted-foreground">
              Carica o scatta una o più foto del volto. Più foto forniscono risultati migliori.
            </p>
            <PhotoUploader
              photos={photos}
              onPhotosChange={handlePhotosChange}
              maxPhotos={10}
            />
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Dati Anagrafici</h3>
            <p className="text-sm text-muted-foreground">
              Inserisci i dati anagrafici della persona.
            </p>
            <PersonForm
              onSubmit={handleFormSubmit}
              isPatient={false}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogClose onClose={handleClose} />
        <DialogHeader>
          <DialogTitle>Aggiungi Nuovo Volto</DialogTitle>
          <DialogDescription>
            Step {currentStep} di {totalSteps}
          </DialogDescription>
          <Progress value={(currentStep / totalSteps) * 100} className="mt-2" />
        </DialogHeader>

        <div className="space-y-6 py-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {renderStep()}

          <div className="flex justify-between pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1 || loading}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Indietro
            </Button>

            {currentStep < totalSteps ? (
              <Button
                type="button"
                onClick={nextStep}
                disabled={loading}
              >
                Avanti
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <Button
                type="button"
                onClick={() => {
                  // Il form gestisce il submit
                  const form = document.querySelector('form');
                  if (form) {
                    form.requestSubmit();
                  }
                }}
                disabled={loading}
              >
                {loading ? 'Salvataggio...' : 'Salva'}
                {!loading && <CheckCircle2 className="h-4 w-4 ml-2" />}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddPersonDialog;
