import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { X, Camera, Upload } from 'lucide-react';

const PhotoUploader = ({ photos = [], onPhotosChange, maxPhotos = 10 }) => {
  const [capturing, setCapturing] = useState(false);
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files || []);
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
      return validTypes.includes(file.type);
    });

    if (validFiles.length === 0) {
      alert('Formato file non supportato. Usa JPG, PNG o WEBP.');
      return;
    }

    const newPhotos = [...photos, ...validFiles].slice(0, maxPhotos);
    onPhotosChange(newPhotos);
    
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCapture = () => {
    if (!webcamRef.current) return;
    
    setCapturing(true);
    const imageSrc = webcamRef.current.getScreenshot();
    
    if (imageSrc) {
      // Converti data URL a File
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], `photo-${Date.now()}.jpg`, { type: 'image/jpeg' });
          const newPhotos = [...photos, file].slice(0, maxPhotos);
          onPhotosChange(newPhotos);
          setCapturing(false);
        })
        .catch(err => {
          console.error('Errore nella cattura:', err);
          setCapturing(false);
        });
    } else {
      setCapturing(false);
    }
  };

  const removePhoto = (index) => {
    const newPhotos = photos.filter((_, i) => i !== index);
    onPhotosChange(newPhotos);
  };

  const getImagePreview = (photo) => {
    if (photo instanceof File) {
      return URL.createObjectURL(photo);
    }
    return photo;
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={() => fileInputRef.current?.click()}
          disabled={photos.length >= maxPhotos}
          className="flex items-center justify-center gap-2 w-full sm:w-auto"
        >
          <Upload className="h-4 w-4" />
          <span className="text-sm sm:text-base">Carica Foto</span>
        </Button>
        
        <Button
          type="button"
          variant="outline"
          onClick={handleCapture}
          disabled={capturing || photos.length >= maxPhotos}
          className="flex items-center justify-center gap-2 w-full sm:w-auto"
        >
          <Camera className="h-4 w-4" />
          <span className="text-sm sm:text-base">{capturing ? 'Scattando...' : 'Scatta Foto'}</span>
        </Button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        multiple
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Webcam nascosta per la cattura */}
      <div className="hidden">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={{
            facingMode: "user"
          }}
        />
      </div>

      {/* Preview delle foto */}
      {photos.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4">
          {photos.map((photo, index) => (
            <Card key={index} className="relative">
              <CardContent className="p-2">
                <div className="relative aspect-square">
                  <img
                    src={getImagePreview(photo)}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-full object-cover rounded-md"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="icon"
                    className="absolute top-1 right-1 h-6 w-6"
                    onClick={() => removePhoto(index)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {photos.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            <p>Nessuna foto caricata. Aggiungi almeno una foto per continuare.</p>
          </CardContent>
        </Card>
      )}

      {photos.length > 0 && (
        <p className="text-sm text-muted-foreground">
          {photos.length} {photos.length === 1 ? 'foto caricata' : 'foto caricate'} 
          {maxPhotos && ` (max ${maxPhotos})`}
        </p>
      )}
    </div>
  );
};

export default PhotoUploader;
