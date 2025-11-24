from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from constants import RelationshipType  

class PersonBase(BaseModel): #TODO: Verificare compatibilità della classe con il nuovo sistema di database, mancanano gli endpoint degli input

    name: str = Field(..., description="Il nome della persona", min_length=2, examples=["Mario"])
    surname: str = Field(..., description="Il cognome della persona", min_length=2, examples=["Rossi"])
    relationship: RelationshipType = Field(..., description="Il tipo di relazione")
    age: Optional[int] = Field(None, gt=0, le=120, description="Età compresa tra 1 e 120 anni", examples=[30])


    @field_validator('name', 'surname')
    @classmethod
    def validate_and_clean_names(cls, v: str) -> str:
        """
        Valida che nome e cognome:
        1. Non siano vuoti.
        2. Non contengano numeri.
        3. Contengano solo lettere o caratteri ammessi (spazio, apostrofo, trattino).
        4. Restituisce la stringa pulita (strip + lower).
        """
        if not v:
            raise ValueError("Il campo non può essere vuoto")
        
        # Controllo numeri
        if any(char.isdigit() for char in v):
            raise ValueError("Non sono ammessi numeri nel nome o cognome")
        
        # Controllo caratteri validi
        valid_chars = set(" '-")
        if not all((char.isalpha() or char in valid_chars) for char in v):
            raise ValueError("Caratteri non validi (ammessi solo lettere, spazi, apostrofi e trattini)")
        
        # Normalizzazione (Pulizia)
        return v.strip().lower()

    # Nota: Non serve un validatore per 'relationship' perché l'Enum lo fa in automatico.
    # Nota: Non serve un validatore custom per 'age' perché 'Field(gt=0, le=120)' lo fa in automatico.


class PersonCreate(PersonBase): #TODO
    """
    Schema usato ESCLUSIVAMENTE per l'INPUT (POST).
    """
    pass


class PersonResponse(PersonBase): #TODO
    """
    Schema usato ESCLUSIVAMENTE per l'OUTPUT (GET).
    """
    # Configurazione fondamentale per leggere i dati dalla classe Person originale
    model_config = ConfigDict(from_attributes=True)


    