import logging
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field, ConfigDict, BeforeValidator, PlainSerializer
from typing import ClassVar, Optional, Any, Annotated
from datetime import date
from bson import ObjectId 
from app.utils.constants import RelationshipType, RoleType

logger = logging.getLogger(__name__)

MAX_LEGHT = 50

PyObjectId = Annotated[
    str | ObjectId,
    BeforeValidator(lambda x: ObjectId(x) if isinstance(x, str) else x),
    PlainSerializer(lambda x: str(x), return_type=str),
]

class Person(BaseModel):
   
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(default="Unknown", min_length=2, max_length=MAX_LEGHT)
    surname: str = Field(default="Unknown", min_length=2, max_length=MAX_LEGHT)
    birthday: date
    relationship: RelationshipType = RelationshipType.ALTRO
    encoding: Optional[dict] = None 
    role: RoleType = RoleType.GUEST   
    
    # Variabile di classe per gestire l'unicità del paziente
    _user_esistente: ClassVar[bool] = False

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True # Permette di usare ObjectId che non è standard Pydantic
    )

    @model_validator(mode='after')
    def check_unico_admin(self):
        # Controllo se stiamo creando un USER (Paziente)
        if self.role == RoleType.USER:
            if Person._user_esistente:
                
                raise ValueError(f"Esiste già un paziente registrato ({RoleType.USER}). Impossibile crearne un altro.")
                       
            Person._user_esistente = True
            logger.info(f"Nuovo Paziente ({RoleType.USER}) registrato: {self.name} {self.surname}")
            
        return self
    

    @field_validator('birthday') 
    @classmethod
    def check_data_passata(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La data di nascita non può essere nel futuro!")
        if v.year < 1900:
            raise ValueError("Data di nascita non valida (troppo indietro nel tempo)")
        return v
    

    @computed_field
    def age(self) -> int:
        today = date.today()
        if not self.birthday:
            return 0
        return today.year - self.birthday.year - (
            (today.month, today.day) < (self.birthday.month, self.birthday.day)
        )

    @classmethod
    def reset_user_slot(cls):
        cls._user_esistente = False
        logger.warning(f"Slot Paziente ({RoleType.USER}) resettato manualmente.")