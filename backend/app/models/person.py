# file: models/person.py

class Person:
    def __init__(self, name: str, surname: str, relationship: str, age: int = None):
        # Qui arrivano dati GIÀ puliti (minuscoli, senza numeri, ecc.)
        self.name = name
        self.surname = surname
        self.relationship = relationship
        self.age = age

    def __repr__(self):
        return f"<Person {self.name} {self.surname} ({self.relationship})>"
