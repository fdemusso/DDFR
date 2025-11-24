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


def IsValidInput(str):
    if any(char.isdigit() for char in str):
        return False

    valid_chars = set(" ' -")  # spazio, apostrofo e trattino
    for char in str:
        if not (char.isalpha() or char in valid_chars):
            return False

    return True

if __name__ == "__main__":
    print(get_surname())