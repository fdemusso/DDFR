from enum import Enum

class RelationshipType(str, Enum):
    """Enumeration of relationship types between persons.

    Defines various relationship types that can exist between a person
    and the primary user in the system.

    """

    MADRE = "madre"
    PADRE = "padre"
    GENITORE = "genitore"
    FRATELLO = "fratello"
    SORELLA = "sorella"
    FIGLIO = "figlio"
    FIGLIA = "figlia"
    AMICO = "amico"
    CONIUGE = "coniuge"
    PARTNER = "partner"
    ASSISTENTE = "assistente"
    MANAGER = "manager"
    ALTRO = "altro"
    COINQUILINO = "coinquilino"
    MEDICO = "medico"
    EMERGENZA = "emergenza"
    MEMBRO_DELLA_FAMIGLIA = "membro della famiglia"
    DOCENTE = "docente"
    BADANTE = "badante"
    TUTORE = "tutore"
    ASSISTENTE_SOCIALE = "assistente sociale"
    SCUOLA = "scuola"
    CENTRO_DIURNO = "centro diurno"

class RoleType(str, Enum):
    """Enumeration of person roles in the system.

    Defines the role types that a person can have within the application.

    """

    USER = "user"
    GUEST = "guest"
