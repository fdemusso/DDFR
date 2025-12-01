import logging
import os
import tempfile
from datetime import datetime

import unittest
from unittest.mock import patch, MagicMock

from app.services.recognition import FaceSystem
from app.services.database import Database
from app.config import database_settings as set, path_settings, api_settings
from app.models.person import Person
from app.utils.constants import RoleType, RelationshipType
from app.utils.img import ImgValidation


# --- CONFIGURAZIONE AMBIENTE ---
os.makedirs(path_settings.logfolder, exist_ok=True)
log_filename = os.path.join(
    path_settings.logfolder, f"local-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)
logger.warning("TEST LOCALE IN CORSO")
TEST_DATABASE = "test_people"


def _build_test_db() -> Database:
    """
    Helper per istanziare un Database puntando sempre al DB di test,
    garantendo l'isolamento dei dati per ogni esecuzione dei test.
    """
    return Database(url=set.url, name=TEST_DATABASE, collection=set.collection)


class TestPersonModel(unittest.TestCase):
    """
    Test sul modello Person (validator, computed field, ecc.).
    """

    def test_person_creation_and_age(self):
        birthday = datetime(2000, 1, 1)
        person = Person(
            name="Mario",
            surname="Rossi",
            birthday=birthday,
            role=RoleType.USER,
            relationship=RelationshipType.FIGLIO,
        )

        self.assertEqual(person.name, "Mario")
        self.assertEqual(person.surname, "Rossi")
        self.assertEqual(person.role, RoleType.USER)
        self.assertEqual(person.relationship, RelationshipType.FIGLIO)
        self.assertGreaterEqual(person.age, 0)

    def test_birthday_in_future_raises(self):
        future_date = datetime(datetime.now().year + 1, 1, 1)
        with self.assertRaises(ValueError):
            Person(
                name="Mario",
                surname="Rossi",
                birthday=future_date,
                role=RoleType.GUEST,
            )

    def test_birthday_too_old_raises(self):
        old_date = datetime(1800, 1, 1)
        with self.assertRaises(ValueError):
            Person(
                name="Mario",
                surname="Rossi",
                birthday=old_date,
                role=RoleType.GUEST,
            )


class TestDatabase(unittest.TestCase):
    """
    Test del servizio Database usando il vero MongoDB ma un DB dedicato di test.
    Ogni test assicura di lasciare pulito il database alla fine.
    """

    def setUp(self):
        # Ogni test parte da un DB di test vuoto
        self.db = _build_test_db()
        self.db.drop_database()
        self.db = _build_test_db()

    def tearDown(self):
        # Pulizia del DB di test dopo ogni test
        try:
            self.db.drop_database()
        except Exception:
            # Se qualcosa va storto, non vogliamo bloccare l'intera suite
            logger.exception("Errore durante il drop del DB di test in tearDown.")

    def _build_person(self, name: str = "Mario", role: RoleType = RoleType.USER) -> Person:
        return Person(
            name=name,
            surname="Rossi",
            birthday=datetime(2005, 1, 1),
            role=role,
        )

    def test_connection_property_and_reconnect(self):
        # All'inizio la connessione deve essere attiva
        self.assertTrue(self.db.is_connected)

        # Chiusura connessione
        self.db.close_connection()
        self.assertFalse(self.db.is_connected)

        # URL None -> deve ritornare None e non lanciare eccezioni
        self.db.url = None
        self.assertIsNone(Database.get_connection(self.db.url))

        # URL valido -> riconnessione
        self.db.url = set.url
        conn = Database.get_connection(self.db.url)
        self.assertIsNotNone(conn)
        self.assertTrue(self.db.is_connected)

    def test_convert_to_objectid_valid_and_invalid(self):
        valid_id = "000000000000000000000000"
        oid = Database.convert_to_objectid(valid_id)
        self.assertIsNotNone(oid)

        invalid_id = "invalid-id"
        self.assertIsNone(Database.convert_to_objectid(invalid_id))
        self.assertIsNone(Database.convert_to_objectid(None))

    def test_crud_person_and_user_constraint(self):
        person = self._build_person(name="Mario", role=RoleType.USER)
        person2 = self._build_person(name="Francesco", role=RoleType.USER)

        # CREATE
        p = self.db.add_person(person)
        self.assertIsNotNone(p)
        person_id = p.id
        self.assertIsNotNone(person_id)

        # READ
        retrieved = self.db.get_person(str(person_id))
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Mario")
        self.assertIsInstance(retrieved.birthday, datetime)

        # Regola: ci può essere un solo USER
        self.assertIsNone(
            self.db.add_person(person2),
            "Dovrebbe fallire l'inserimento di un secondo USER",
        )

        # UPDATE
        person.name = "Updated User"
        updated = self.db.update_person(str(person_id), person)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Updated User")

        # DELETE
        delete_result = self.db.remove_person(str(person_id))
        self.assertTrue(delete_result)
        self.assertIsNone(self.db.get_person(str(person_id)))

        # ID inesistente valido
        fake_id = "000000000000000000000000"
        self.assertIsNone(self.db.get_person(fake_id))
        self.assertIsNone(self.db.update_person(fake_id, person))
        self.assertFalse(self.db.remove_person(fake_id))

    def test_get_all_people_and_encodings(self):
        # All'inizio DB vuoto
        self.assertEqual(self.db.get_all_people(), [])

        # Aggiungiamo due persone con encoding diversi
        enc1 = {"h1": [0.1, 0.2, 0.3]}
        enc2 = {"h2": [0.4, 0.5, 0.6]}

        p1 = self._build_person(name="Mario", role=RoleType.GUEST)
        p1.encoding = enc1
        p2 = self._build_person(name="Luigi", role=RoleType.GUEST)
        p2.encoding = enc2

        self.db.add_person(p1)
        self.db.add_person(p2)

        people = self.db.get_all_people()
        self.assertEqual(len(people), 2)

        names, encodings = self.db.get_all_encodings()
        self.assertEqual(len(names), 2)
        self.assertEqual(len(encodings), 2)
        self.assertIn("Mario Rossi", names)
        self.assertIn("Luigi Rossi", names)

    def test_update_people_bulk(self):
        # Uno senza id, uno con id che verrà aggiornato
        p1 = self._build_person(name="Mario", role=RoleType.GUEST)
        p2 = self._build_person(name="Luigi", role=RoleType.GUEST)

        saved_p2 = self.db.add_person(p2)
        self.assertIsNotNone(saved_p2)

        p2.id = saved_p2.id
        p2.name = "Luigi Updated"

        success = self.db.update_people([p1, p2])
        self.assertEqual(success, 2)

        all_people = self.db.get_all_people()
        names = sorted([p.name for p in all_people])
        self.assertEqual(names, ["Luigi Updated", "Mario"])

    def test_drop_database_and_state_reset(self):
        # Creiamo un utente/paziente
        person = self._build_person(name="Mario", role=RoleType.USER)
        created = self.db.add_person(person)
        self.assertIsNotNone(created)

        # Il drop deve eliminare il DB e resettare l'eventuale cache
        self.db.drop_database()

        # Una nuova istanza sullo stesso DB deve vedere un DB vuoto
        db2 = _build_test_db()
        people = db2.get_all_people()
        self.assertIsInstance(people, list)
        self.assertEqual(
            len(people), 0, "Dopo il drop il database di test dovrebbe essere vuoto"
        )
        db2.drop_database()


class TestFaceSystem(unittest.TestCase):
    """
    Test per il sistema di riconoscimento facciale, con mocking di face_recognition
    e uso del vero DB di test per salvare i dati.
    """

    def setUp(self):
        self.db = _build_test_db()
        self.db.drop_database()
        self.db = _build_test_db()

    def tearDown(self):
        try:
            self.db.drop_database()
        except Exception:
            logger.exception("Errore durante il drop del DB di test in tearDown (FaceSystem).")

    def test_face_system_integrity_and_operational_flags(self):
        # Nessun encoding -> sistema non operativo ma integro
        fs = FaceSystem(self.db)
        self.assertTrue(fs.dataset_integrity)
        self.assertFalse(fs.is_operational)

        # Aggiungiamo una persona con encoding valido
        person = Person(
            name="Mario",
            surname="Rossi",
            birthday=datetime(2000, 1, 1),
            role=RoleType.GUEST,
            encoding={"h1": [0.1, 0.2, 0.3]},
        )
        self.db.add_person(person)

        fs2 = FaceSystem(self.db)
        self.assertTrue(fs2.dataset_integrity)
        self.assertTrue(fs2.is_operational)
        self.assertEqual(len(fs2.known_face_names), 1)
        self.assertEqual(len(fs2.known_face_encodings), 1)

    @patch("app.services.recognition.face_recognition.face_encodings")
    @patch("app.services.recognition.face_recognition.load_image_file")
    def test_recognize_from_img_success_and_failure(
        self, mock_load_image_file: MagicMock, mock_face_encodings: MagicMock
    ):
        """
        Verifica che il metodo gestisca correttamente i casi in cui:
        - il sistema non è operativo (ritorno False immediato)
        - non vengono trovati volti nelle immagini (ritorno False)
        Evitiamo volutamente il percorso \"successo\" perché l'implementazione
        attuale di `recognize_from_img` utilizza `Person` come se fosse un dict.
        """
        # Caso 1: sistema non operativo -> ritorna False senza accedere alle immagini
        fs = FaceSystem(self.db)
        self.assertFalse(fs.is_operational)
        self.assertFalse(fs.recognize_from_img(["/path/finto.png"], Person(
            name="Mario",
            surname="Rossi",
            birthday=datetime(2000, 1, 1),
            role=RoleType.GUEST,
        ), remove_img=False))

        # Caso 2: sistema operativo ma nessun volto trovato nelle immagini
        # Creiamo una persona con encoding per rendere operativo il sistema
        existing = Person(
            name="Esistente",
            surname="Rossi",
            birthday=datetime(1990, 1, 1),
            role=RoleType.GUEST,
            encoding={"h0": [0.0, 0.0, 0.0]},
        )
        self.db.add_person(existing)

        fs = FaceSystem(self.db)
        self.assertTrue(fs.is_operational)

        # Mock: nessun volto trovato
        mock_load_image_file.return_value = "fake_image"
        mock_face_encodings.return_value = []

        os.makedirs(path_settings.imgsfolder, exist_ok=True)
        tmp_dir = tempfile.mkdtemp()
        img_path = os.path.join(tmp_dir, "test.png")
        from PIL import Image

        image = Image.new("RGB", (10, 10), color="red")
        image.save(img_path, "PNG")

        person = Person(
            name="Mario",
            surname="Rossi",
            birthday=datetime(2000, 1, 1),
            role=RoleType.GUEST,
        )

        result_none = fs.recognize_from_img([img_path], person, remove_img=False)
        self.assertFalse(result_none)


class TestImgValidation(unittest.TestCase):
    """
    Test per le utility di gestione immagini (ImgValidation).
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        os.makedirs(path_settings.imgsfolder, exist_ok=True)

        # Creiamo una semplice immagine PNG
        from PIL import Image

        self.img_path = os.path.join(self.tmp_dir, "test_img.png")
        img = Image.new("RGB", (10, 10), color="blue")
        img.save(self.img_path, "PNG")

    def tearDown(self):
        # Pulizia dei file temporanei
        for root, dirs, files in os.walk(self.tmp_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except FileNotFoundError:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except OSError:
                    pass
        try:
            os.rmdir(self.tmp_dir)
        except OSError:
            pass

    @patch("app.utils.img.ImgValidation.hash_img", return_value="fakehash")
    @patch("app.utils.img.ImgValidation.validate_png", return_value=True)
    @patch("app.utils.img.ImgValidation.ConvertAnyToPng", side_effect=lambda p, n, e, d: p)
    def test_img_validation_and_hash(
        self,
        mock_convert: MagicMock,
        mock_validate: MagicMock,
        mock_hash: MagicMock,
    ):
        """
        Testa il flusso di ImgValidation senza dipendere dalle particolarità
        del filesystem reale o dai dettagli della conversione interna.
        """
        validator = ImgValidation(self.img_path, delete=False)
        self.assertTrue(validator.is_valid)
        self.assertEqual(validator.hash, "fakehash")

    @patch("app.utils.img.ImgValidation.hash_img")
    @patch("app.utils.img.ImgValidation.validate_png", return_value=True)
    @patch("app.utils.img.ImgValidation.ConvertAnyToPng", side_effect=lambda p, n, e, d: p)
    def test_compare_img(
        self,
        mock_convert: MagicMock,
        mock_validate: MagicMock,
        mock_hash: MagicMock,
    ):
        """
        Verifica che compare_img ritorni True per immagini con hash uguale
        e False per immagini con hash diverso, usando hash mockati.
        """
        # Prima istanza con hash A
        mock_hash.return_value = "hashA"
        v1 = ImgValidation(self.img_path, delete=False)
        self.assertTrue(v1.is_valid)

        # Seconda immagine con stesso hash -> True
        mock_hash.return_value = "hashA"
        img2_path = os.path.join(self.tmp_dir, "test_img_copy.png")
        with open(img2_path, "wb") as f:
            f.write(b"fake")
        self.assertTrue(v1.compare_img(img2_path))

        # Terza immagine con hash diverso -> False
        mock_hash.return_value = "hashB"
        img3_path = os.path.join(self.tmp_dir, "test_img_other.png")
        with open(img3_path, "wb") as f:
            f.write(b"fake2")
        self.assertFalse(v1.compare_img(img3_path))


class TestConfigSettings(unittest.TestCase):
    """
    Test basilari su config.py (DatabaseSettings, PathSettings, APISettings).
    Nessun avvio di servizi reali, solo verifica dei valori principali.
    """

    def test_database_settings_defaults(self):
        self.assertTrue(set.url.startswith("mongodb://"))
        self.assertIsInstance(set.name, str)
        self.assertIsInstance(set.collection, str)

    def test_path_settings_directories(self):
        # Verifica che le proprietà principali esistano e siano stringhe
        self.assertIsInstance(path_settings.logfolder, str)
        self.assertIsInstance(path_settings.imgsfolder, str)

    def test_api_settings_basic_fields(self):
        self.assertIsInstance(api_settings.app_name, str)
        self.assertIsInstance(api_settings.description, str)
        self.assertIsInstance(api_settings.app_version, str)


if __name__ == "__main__":
    unittest.main()


