import logging
from pydantic import BaseModel, Field, field_validator, computed_field, ConfigDict, BeforeValidator, PlainSerializer
from typing import Optional, Annotated
from datetime import date, datetime 
from bson import ObjectId 
from utils.constants import RelationshipType, RoleType

logger = logging.getLogger(__name__)

MAX_LENGTH = 50

PyObjectId = Annotated[
    str | ObjectId,
    BeforeValidator(lambda x: ObjectId(x) if isinstance(x, str) else x),
    PlainSerializer(lambda x: str(x), return_type=str),
]

class Person(BaseModel):
    """Person data model for face recognition system.

    Represents a person with personal information, face encodings, and relationship data.
    Uses Pydantic for validation and serialization, compatible with MongoDB ObjectId.

    Attributes:
        id (Optional[PyObjectId]): MongoDB document ID. Default: None.
        name (str): Person's first name. Default: "Unknown", length 2-50.
        surname (str): Person's last name. Default: "Unknown", length 2-50.
        birthday (datetime): Person's date of birth. Required, must be valid date.
        relationship (RelationshipType): Relationship type to the user. Default: ALTRO.
        encoding (Optional[dict]): Dictionary of face encodings (hash -> embedding vector). Default: None.
        role (RoleType): Person's role in the system. Default: GUEST.

    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(default="Unknown", min_length=2, max_length=MAX_LENGTH)
    surname: str = Field(default="Unknown", min_length=2, max_length=MAX_LENGTH)
    
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
        """Validate that birthday is a valid past date.

        Checks that the birthday is not in the future and not before year 1900.

        Args:
            v (datetime): The birthday datetime to validate.

        Returns:
            datetime: The validated birthday datetime.

        Raises:
            ValueError: If birthday is in the future or before year 1900.

        """
        if v.date() > date.today():
            raise ValueError("La data di nascita non può essere nel futuro!")
        
        if v.year < 1900:
            raise ValueError("Data di nascita non valida (troppo indietro nel tempo)")
        
        return v
    

    @computed_field
    def age(self) -> int:
        """Calculate person's age based on birthday.

        Computes age as the difference between current date and birthday,
        accounting for whether the birthday has occurred this year.

        Returns:
            int: Person's age in years. Returns 0 if birthday is not set.

        """
        today = date.today()
        if not self.birthday:
            return 0
        
        return today.year - self.birthday.year - (
            (today.month, today.day) < (self.birthday.month, self.birthday.day)
        )