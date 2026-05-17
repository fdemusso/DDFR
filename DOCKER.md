# Docker Setup

DDFR ships with a fully configured `docker-compose.yml`. A single command starts the entire stack — MongoDB, the Python backend, and the React frontend — with no manual configuration needed.

## Requirements

[Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

## Start

```bash
git clone https://github.com/fdemusso/DDFR.git
cd DDFR
docker-compose up --build
```

Open **http://localhost:3000** in your browser.

> **First run:** the InsightFace `buffalo_l` model downloads automatically (~300 MB). Subsequent starts skip this step and are fast.

## Services

| Service | URL | Notes |
| --- | --- | --- |
| Frontend (React) | http://localhost:3000 | Served by nginx |
| Backend (FastAPI) | http://localhost:8000 | REST API + WebSocket |
| MongoDB | localhost:27017 | Persisted via Docker volume |

## Configuration

The backend reads `backend/.env.docker`, which is committed to the repository with safe defaults. You can edit it to tune recognition tolerance, enable debug logging, etc.

`docker-compose.yml` overrides `DB_URL`, `DB_NAME`, and `DB_COLLECTION` via its `environment` section so the backend connects to the Docker-internal MongoDB service regardless of what is in `.env.docker`.

### Key variables

| Variable | Default | Description |
| --- | --- | --- |
| `APP_TOLLERANCE` | `0.45` | Face recognition distance threshold. Lower = stricter matching. |
| `APP_DEBUG` | `false` | Enable verbose request/response logging. |
| `DB_HASH` | *(pre-filled)* | Legacy field kept for backward compatibility. |

## Data Persistence

Data is stored in named Docker volumes and survives container restarts:

| Volume | Contents |
| --- | --- |
| `mongodb_data` | MongoDB documents (people registry + face embeddings) |
| `backend_logs` | Backend application logs |
| `backend_img` | Stored face images |

To wipe all data and start fresh:

```bash
docker-compose down -v
```

> **Warning:** this permanently deletes all enrolled faces and person records.

## Webcam & HTTPS

The webcam is accessed by the **browser**, not the Docker containers. On `localhost`, browsers allow camera access without HTTPS — the default Docker setup works out of the box.

If you deploy DDFR on a remote server or non-localhost URL, you will need HTTPS. See the [HTTPS Setup](README.md#https-setup) section in the main README.

## Useful Commands

```bash
# Start all services in the background
docker-compose up -d --build

# Stop all services (data is preserved)
docker-compose down

# Follow live logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild and restart a single service
docker-compose build backend
docker-compose up -d backend

# Open a shell in a running container
docker-compose exec backend bash
docker-compose exec mongodb mongosh

# Check service health
docker-compose ps

# MongoDB backup
docker-compose exec mongodb mongodump --out /data/backup
docker cp ddfr_mongodb:/data/backup ./backup
```

## Troubleshooting

**Backend exits immediately after start**  
The backend waits for MongoDB's health check to pass (up to ~40 s on first run). If it exits, run `docker-compose logs backend` to read the error.

**`docker-compose up` fails with "Docker daemon not running"**  
Start Docker Desktop and wait for it to report "Docker is running" in the system tray.

**Port already in use**  
Change the host port in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # access frontend at localhost:3001
```

**Build fails with out-of-memory errors**  
Increase Docker Desktop memory (Settings → Resources → Memory). The build requires ~2 GB RAM.

**InsightFace model download fails**  
The backend downloads models from a CDN on first run. Make sure Docker containers have outbound internet access (check firewall/proxy settings).

**No faces recognized after enrolling someone**  
Check `APP_TOLLERANCE` in `backend/.env.docker`. The default is `0.45` — lower values require a closer match. Try increasing to `0.55` if recognition is too strict.
