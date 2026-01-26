import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import PhotoUploader from './PhotoUploader';
import PersonForm from './PersonForm';
import { ChevronRight, ChevronLeft, CheckCircle2, AlertCircle } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const SetupWizard = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [photos, setPhotos] = useState([]);
  const [formData, setFormData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const totalSteps = 4;

  const handlePhotosChange = (newPhotos) => {
    setPhotos(newPhotos);
  };

  const handleFormSubmit = (data) => {
    setFormData(data);
    setCurrentStep(4);
  };

  const handleFinalSubmit = async () => {
    if (photos.length === 0) {
      setError('Devi caricare almeno una foto');
      setCurrentStep(2);
      return;
    }

    if (!formData) {
      setError('Devi compilare tutti i dati');
      setCurrentStep(3);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Prepara FormData
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('surname', formData.surname);
      formDataToSend.append('birthday', formData.birthday);
      formDataToSend.append('relationship', formData.relationship);
      formDataToSend.append('role', 'user'); // Sempre USER per setup iniziale

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
      console.log('Paziente creato:', result);
      
      // Completa il setup
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      setError(err.message || 'Errore durante il salvataggio del paziente');
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
            <h2 className="text-2xl font-bold">Benvenuto nel Sistema di Riconoscimento Facciale</h2>
            <p className="text-muted-foreground">
              Per iniziare, dobbiamo configurare il profilo del paziente. Questo processo richiederà:
            </p>
            <ul className="list-disc list-inside space-y-2 text-muted-foreground">
              <li>Caricamento di una o più foto del volto del paziente</li>
              <li>Inserimento dei dati anagrafici</li>
              <li>Conferma e salvataggio</li>
            </ul>
            <p className="text-sm text-muted-foreground">
              <strong>Suggerimento:</strong> Per migliori risultati, carica foto con buona illuminazione 
              e dove il volto è chiaramente visibile.
            </p>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Carica le Foto del Volto</h2>
            <p className="text-muted-foreground">
              Carica o scatta una o più foto del volto del paziente. Più foto forniscono risultati migliori.
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
            <h2 className="text-2xl font-bold">Dati Anagrafici</h2>
            <p className="text-muted-foreground">
              Inserisci i dati anagrafici del paziente.
            </p>
            <PersonForm
              onSubmit={handleFormSubmit}
              isPatient={true}
            />
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Riepilogo e Conferma</h2>
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Dati Anagrafici</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Nome</dt>
                      <dd className="text-sm">{formData?.name}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Cognome</dt>
                      <dd className="text-sm">{formData?.surname}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Data di Nascita</dt>
                      <dd className="text-sm">{formData?.birthday ? new Date(formData.birthday).toLocaleDateString('it-IT') : ''}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Relazione</dt>
                      <dd className="text-sm">{formData?.relationship}</dd>
                    </div>
                  </dl>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Foto Caricate</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {photos.length} {photos.length === 1 ? 'foto' : 'foto'} pronta per l'elaborazione
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Configurazione Iniziale</CardTitle>
          <CardDescription>
            Step {currentStep} di {totalSteps}
          </CardDescription>
          <Progress value={(currentStep / totalSteps) * 100} className="mt-4" />
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {renderStep()}

          <div className="flex justify-between pt-4">
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
                onClick={handleFinalSubmit}
                disabled={loading}
              >
                {loading ? 'Salvataggio...' : 'Conferma e Salva'}
                {!loading && <CheckCircle2 className="h-4 w-4 ml-2" />}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SetupWizard;
