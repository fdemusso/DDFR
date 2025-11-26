from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import backend.app.services.database as db_service
app = FastAPI()

MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "FaceAuthDB"
COLLECTION_NAME = "Users"

try:
    db = Database(url=MONGO_URL, name=DB_NAME, collection=COLLECTION_NAME)
    if db.is_connected:
        print("Siamo online e connessi a MongoDB!")
except Exception as e:
    print(f"Errore critico di connessione: {e}")

#importare tutti i dati dal db
people=db.get_collection()

@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/people")
def create_item(people:dict):
    new_person={
        name: people['name'],
        surname: people['name']
    }

    people.append(new_person)
    db.add_person(new_person)
    return new_person

@app.get("/people")
def get_people():
    return people
    
#servirebbe una funzione per semplificare l'id
@app.get("/people/{person_id}")
def get_person():
    for person in people:
        if person["id"]==person_id:
            return person 


@app.put("/people/{person_id}")
def update_person(person_id: str, updated_data: dict):
    for person in people:
        if person["id"] == person_id:
            person.update(updated_data)
            db.update_person(person_id, updated_data)
            return person
    raise HTTPException(status_code=404, detail="Person not found")

@app.delete("/people/{person_id}")
def delete_person(person_id: str):
    for index, person in enumerate(people):
        if person["id"] == person_id:
            del people[index]
            db.remove_person(person_id)
            return {"detail": "Person deleted"}
    raise HTTPException(status_code=404, detail="Person not found")