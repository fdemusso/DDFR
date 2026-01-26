# Guida Docker per DDFR

Questa guida spiega come avviare il progetto DDFR utilizzando Docker e Docker Compose.

## Prerequisiti

- Docker Desktop installato e avviato
- Docker Compose v3.8 o superiore

## Struttura Docker

Il progetto è composto da 3 servizi:

- **mongodb**: Database MongoDB
- **backend**: API FastAPI per il riconoscimento facciale
- **frontend**: Applicazione React

## Configurazione Iniziale

### 1. File .env Backend

Crea il file `.env` nella directory `backend/app/` basandoti su `backend/example.env.txt`:

```bash
cp backend/example.env.txt backend/app/.env
```

Modifica `backend/app/.env` con queste impostazioni per Docker:

```env
DB_URL=mongodb://mongodb:27017/
DB_NAME=ddfr_db
DB_COLLECTION=people
DB_HASH="300a31fbdc6f3ff4fb27625c2ed49fdc"

LOG_LOGFOLDER=logs

APP_NAME=DDFR API
APP_VERSION=1.0.0
APP_DESCRIPTION=API per il riconoscimento facciale e la gestione delle persone
APP_TOLLERANCE=0.45
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
APP_USE_HTTPS=false
```

**Nota importante**: `DB_URL` deve usare `mongodb://mongodb:27017/` (nome del servizio Docker) invece di `localhost`.

## Avvio del Progetto

### Avvio completo

```bash
docker-compose up --build
```

Questo comando:
- Costruisce le immagini Docker per backend e frontend
- Avvia tutti i servizi (mongodb, backend, frontend)
- Mostra i log di tutti i container

### Avvio in background

```bash
docker-compose up -d --build
```

### Visualizzazione log

```bash
# Tutti i servizi
docker-compose logs -f

# Singolo servizio
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

## Accesso all'Applicazione

Dopo l'avvio, l'applicazione sarà disponibile su:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **MongoDB**: localhost:27017

## Webcam

La webcam viene acceduta direttamente dal browser dell'utente, non dal container Docker. Quando apri http://localhost:3000 nel browser, ti verrà chiesta l'autorizzazione per accedere alla webcam.

## Gestione dei Dati

### Volumi Docker

I dati vengono salvati in volumi Docker persistenti:

- `mongodb_data`: Database MongoDB
- `backend_logs`: Log del backend
- `backend_img`: Immagini salvate dal backend

### Backup MongoDB

Per fare backup del database:

```bash
docker-compose exec mongodb mongodump --out /data/backup
docker cp ddfr_mongodb:/data/backup ./backup
```

### Reset completo

Per eliminare tutti i dati e ricominciare:

```bash
docker-compose down -v
```

**Attenzione**: Questo elimina tutti i volumi e i dati salvati!

## Comandi Utili

### Stop dei servizi

```bash
docker-compose stop
```

### Riavvio dei servizi

```bash
docker-compose restart
```

### Ricostruzione di un singolo servizio

```bash
docker-compose build backend
docker-compose up -d backend
```

### Accesso al container

```bash
# Backend
docker-compose exec backend bash

# MongoDB
docker-compose exec mongodb mongosh
```

### Verifica stato servizi

```bash
docker-compose ps
```

## Troubleshooting

### Backend non si connette a MongoDB

Verifica che:
1. Il servizio `mongodb` sia avviato: `docker-compose ps`
2. Il `DB_URL` nel file `.env` sia `mongodb://mongodb:27017/`
3. I servizi siano sulla stessa rete Docker (gestito automaticamente da docker-compose)

### Frontend non si connette al backend

Verifica che:
1. Il backend sia avviato e risponda su http://localhost:8000
2. Le variabili WebSocket nel `docker-compose.yml` siano corrette:
   - `REACT_APP_WS_HOST=localhost` (per accesso dal browser)
   - `REACT_APP_WS_PORT=8000`

### Errori durante il build

Se ci sono errori durante il build:

1. Verifica che Docker abbia abbastanza risorse (RAM, spazio disco)
2. Prova a ricostruire senza cache: `docker-compose build --no-cache`
3. Verifica i log: `docker-compose build`

### Porta già in uso

Se una porta è già in uso, modifica le porte nel `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Cambia 3000 in 3001
```

## Sviluppo

Per sviluppo con hot-reload, puoi montare il codice sorgente come volume nel `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./backend/app:/app/app
```

Tuttavia, per semplicità, questa configurazione usa build di produzione.

## Note

- I modelli InsightFace vengono scaricati automaticamente al primo avvio del backend
- I log del backend sono salvati nel volume `backend_logs`
- MongoDB non richiede autenticazione in questa configurazione (solo per sviluppo locale)
