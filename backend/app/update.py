from app.config import database_settings as set
from app.services import database
import app.services.recognition as fr
import app.utils.img as img_util
import logging
import os 

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_flavio():
    """
    Funzione di aggiornamento per la versione 'flavio'.
    Aggiunge eventuali modifiche necessarie al database o alla configurazione.
    """
    try:
        # Esempio: Verifica connessione al database
        DATASET = database.Database(
            url=set.url,
            name=set.name,
            collection=set.collection,
        )
        faces = fr.FaceSystem(DATASET)

        p= faces.client.get_person("692f04e1ad50b2b0e8c19d12")
        if p:
            logger.info(f"Persona trovata: {p.name} {p.surname}, età: {p.age}")
        else:
            logger.warning("Persona con ID specificato non trovata nel database.")
            return

        # aggiorno flavio con altri volti 
        
        cartella_flavio = "/Users/flaviodemusso/Desktop/DDFR/backend/app/img/flavio"
        cartella_img = "/Users/flaviodemusso/Desktop/DDFR/backend/app/img"
        
        # Prima cerca nella cartella flavio (HEIC da convertire)
        nuovi_volti = []
        if os.path.exists(cartella_flavio):
            for filename in os.listdir(cartella_flavio):
                percorso_completo = os.path.join(cartella_flavio, filename)
                if os.path.isfile(percorso_completo):
                    nuovi_volti.append(percorso_completo)
        
        # Poi cerca PNG già convertiti nella cartella img principale
        if os.path.exists(cartella_img):
            for filename in os.listdir(cartella_img):
                if filename.lower().endswith('.png') and filename.startswith('IMG_'):
                    percorso_completo = os.path.join(cartella_img, filename)
                    if os.path.isfile(percorso_completo):
                        nuovi_volti.append(percorso_completo)


        
            
        if nuovi_volti:
            logger.info(f"Trovate {len(nuovi_volti)} immagini da processare")
            if faces.recognize_from_img(nuovi_volti, p, remove_img=True):
                # Verifica finale che i volti siano stati aggiunti
                p_aggiornato = faces.client.get_person("692f04e1ad50b2b0e8c19d12")
                if p_aggiornato and p_aggiornato.encoding:
                    num_encoding = len(p_aggiornato.encoding)
                    logger.info(f"✓ Volti aggiunti con successo! Totale encoding per {p_aggiornato.name}: {num_encoding}")
                else:
                    logger.warning("⚠ Persona aggiornata ma encoding non trovato")
            else:
                logger.warning("Nessun nuovo volto aggiunto per 'flavio'.")
        else:
            logger.warning("Nessuna immagine trovata nella cartella flavio.")


        if faces.is_operational:
            logger.info("Aggiornamento 'flavio' completato con successo.")
        else:
            logger.warning("Aggiornamento 'flavio' completato, ma il sistema non è operativo.")
    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento 'flavio': {e}")


if __name__ == "__main__":
    update_flavio()