import logging
from pydantic import BaseModel, Field, field_validator, computed_field, ConfigDict, BeforeValidator, PlainSerializer
from typing import Optional, Annotated
from datetime import date, datetime 
from bson import ObjectId 
from utils.constants import RelationshipType, RoleType

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
    
    birthday: datetime 
    
    relationship: RelationshipType = RelationshipType.ALTRO
    encoding: Optional[dict] = None 
    role: RoleType = RoleType.GUEST   
    

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True 
    )
    

    @field_validator('birthday') 
    @classmethod
    def check_data_passata(cls, v: datetime) -> datetime:
        if v.date() > date.today():
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