import logging 
import os
logger = logging.getLogger(__name__)

def clear():
    if os.name == "nt":       # Windows
        os.system("cls")
    else:                     # macOS o Linux
        os.system("clear")

def IsValidInput(str):
    if any(char.isdigit() for char in str):
        return False

    valid_chars = set(" ' -")  # spazio, apostrofo e trattino
    for char in str:
        if not (char.isalpha() or char in valid_chars):
            return False

    return True

def get_name():

    flag = True
    while flag:
        name = input("Inserisci il cognome della persona: ").lower()
        if IsValidInput(name) and len(name) <= 25 and len(name) > 0:
            flag = False
            return name
        elif len(name) == 0:
            print("assegnato sconosciuto")
            name = "unknown surname"
            flag = False
            return name

        else:
            print("Cognome non valido. Inserisci solo lettere (max 20 caratteri).")
            
    return None

def get_surname():

    flag = True
    while flag:
        surname = input("Inserisci il cognome della persona: ").lower()
        if IsValidInput(surname) and len(surname) <= 25 and len(surname) > 0:
            flag = False
            return surname
        elif len(surname) == 0:
            print("assegnato sconosciuto")
            surname = "unknown surname"
            flag = False
            return surname

        else:
            print("Cognome non valido. Inserisci solo lettere (max 20 caratteri).")
            
    return None

def get_age():

    flag = False
    while not flag:
        try:
            age = int(input("Inserisci l'età della persona: ").strip())
            if 0 < age <= 120:
                logging.info(f"Età accettata: {age}")
                flag = True
            elif age == 0 or None:
                print("assegnato sconosciuto")
                age = "unknown age"
                flag = True
                clear()
            else:
                print("Età non valida. Inserisci un numero tra 1 e 120.")
                clear()
        except ValueError:
            print("Età non valida. Inserisci un numero tra 1 e 120.")
            clear()

    return age

def get_relationship():

    flag = False
    relationships = ["madre", "padre", "genitore", "fratello", "sorella", "figlio", "figlia", "amico", 
                     "coniuge", "partner", "assistente", "manager", "altro", "coinquilino","medico",
                     "emergenza", "membro della famiglia","docente","badante","tutore","assistente sociale","scuola","centro diurno"]
            
    while not flag:
        relationship = input("Inserisci il rapporto con la persona (es. amico, familiare): ").strip().lower()
        if relationship in relationships:
            logging.info(f"Rapporto accettato: {relationship}")
            flag = True
        elif relationship == "help":
            clear()
            print("Rapporti disponibili:")
            for rel in relationships:
                print(f"- {rel.capitalize()}")
        elif len(relationship) == 0:
            print("assegnato sconosciuto")
            relationship = "unknown relationship"
            flag = True
            clear()
        else:
            print("Rapporto non valido. Inserisci solo lettere (digita help per vedere i disponibili).")
            clear()

    return relationship