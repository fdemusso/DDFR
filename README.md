<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=5cb85c&height=200&section=header&text=DDFR&fontSize=90&fontColor=FFFFFF&animation=fadeIn" />

  **Digital Dementia Face Recognition**

  [![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
  [![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
  [![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
  [![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue?style=flat-square)](LICENSE)

</div>

---

Memory is the quiet thread that weaves the tapestry of our identity. **DDFR** is an open-source, real-time face recognition system designed as a **digital memory extension for people living with dementia**.

When a known face appears before the camera, the system identifies them instantly — bridging the cognitive gap and turning the anxiety of the unknown into the comfort of familiarity.

---

## Table of Contents

- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Technical Highlights](#technical-highlights)
- [Tech Stack](#tech-stack)
- [Enrolling a Face](#enrolling-a-face)
- [HTTPS Setup](#https-setup)
- [Local Development](#local-development)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

The fastest way to run DDFR is with Docker. No Python or Node.js installation required.

**Requirement:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/fdemusso/DDFR.git
cd DDFR
docker-compose up --build
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

> **First run:** the InsightFace `buffalo_l` model downloads automatically (~300 MB). Subsequent starts are instant.  
> **Webcam:** browsers grant camera access to `localhost` without HTTPS — see [HTTPS Setup](#https-setup) for remote deployment.

For more Docker commands and configuration options, see [DOCKER.md](DOCKER.md).

---

## How It Works

DDFR streams live video frames through a three-stage AI pipeline over WebSocket:

```
 Browser (React 19)
    │
    │  WebSocket — binary JPEG frames at ~13 fps
    ▼
 FastAPI + Uvicorn (Python 3.11)
    │
    │  ThreadPoolExecutor — frame processing off the async loop
    ▼
 InsightFace buffalo_l
    │  Face detection + 512-dim ArcFace embeddings
    ▼
 FAISS vector index
    │  L2 nearest-neighbor search on normalized embeddings
    ▼
 MongoDB
    │  Resolve person metadata (name, relationship, age)
    ▼
 WebSocket response → bounding box coordinates + person labels
```

The round-trip — from frame sent to annotated result rendered — targets sub-100 ms on commodity hardware.

---

## Architecture

```
DDFR/
├── backend/
│   ├── app/
│   │   ├── main.py            # ASGI app: lifespan, CORS, SSL, router wiring
│   │   ├── config.py          # Pydantic Settings — prefix-scoped env vars
│   │   ├── routers/
│   │   │   ├── route.py       # REST: person CRUD, /api/status
│   │   │   └── websocket.py   # WS /ws: frame ingestion → detection → response
│   │   └── services/
│   │       ├── recognition.py # InsightFace + FAISS engine (singleton)
│   │       └── database.py    # MongoDB CRUD, embedding serialization
│   └── requirements/
│       ├── base.txt           # Core deps
│       ├── docker.txt         # + ONNX Runtime CPU + FAISS CPU
│       ├── nvidia.txt         # + onnxruntime-gpu + FAISS GPU
│       ├── mac.txt            # + CoreML acceleration
│       └── universal.txt      # + DirectML (Windows)
│
└── frontend/
    └── src/
        ├── hooks/
        │   ├── useWebSocket.js    # WS lifecycle, exponential backoff reconnect
        │   ├── useWebcam.js       # Camera capture, frame-rate throttling
        │   ├── useFaceDetection.js
        │   └── useLatency.js
        └── components/
            ├── WebcamView.js
            ├── FaceBox.js         # SVG bounding boxes with person labels
            └── AddPersonDialog.js # Face enrollment form
```

---

## Technical Highlights

| Area | Detail |
|---|---|
| **Real-time pipeline** | WebSocket over ASGI; binary JPEG transfer; ~13 fps frame rate throttled client-side to prevent queue buildup |
| **Face recognition** | InsightFace `buffalo_l` — state-of-the-art detection + 512-dim ArcFace embeddings |
| **Vector search** | FAISS L2 nearest-neighbor; cosine-equivalent on normalized embeddings |
| **Hardware acceleration** | Auto-selects at runtime: CUDA GPU → Apple CoreML → Windows DirectML → CPU fallback |
| **Docker** | Multi-stage builds (Node builder → nginx; Python slim + system deps); health-check dependency ordering |
| **WebSocket resilience** | Exponential backoff reconnect (3 s base → 15 s cap); in-flight lock prevents frame-over-frame accumulation |
| **Configuration** | Pydantic Settings with prefix-scoped env vars (`DB_`, `APP_`, `LOG_`) — zero code changes across environments |
| **Frontend architecture** | Custom hooks decouple camera capture, WebSocket state, face detection, and latency measurement |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Tailwind CSS, Shadcn-style components, WebSocket API |
| **Backend** | Python 3.11, FastAPI, Uvicorn (ASGI) |
| **AI / Vision** | InsightFace, ONNX Runtime, FAISS |
| **Database** | MongoDB, PyMongo |
| **Infrastructure** | Docker, docker-compose, nginx, GitHub Actions |

---

## Enrolling a Face

Before the system can recognize someone, they must be registered:

1. Open **http://localhost:3000**
2. Click **Add Person** (or follow the Setup Wizard on first launch)
3. Enter name, relationship, and age
4. Upload or capture face photos — DDFR extracts and stores the 512-dim embedding in MongoDB
5. The person is immediately available for recognition in the live camera feed

---

## HTTPS Setup

> **Docker on localhost — HTTPS is not required.** Modern browsers grant webcam access to `localhost` without a secure context. The default `docker-compose up` setup works out of the box.

HTTPS is only needed when accessing DDFR from a **non-localhost URL** (remote server, IP address, or custom hostname on a LAN).

### Option A — mkcert (recommended for LAN / development)

[mkcert](https://github.com/FiloSottile/mkcert) generates locally-trusted certificates that browsers accept without warnings.

```bash
# Install mkcert (see https://github.com/FiloSottile/mkcert#installation)
mkcert -install
mkcert ddfr.local localhost 127.0.0.1

# Generates: ddfr.local+2.pem  ddfr.local+2-key.pem
```

Add to `backend/app/.env`:
```env
APP_USE_HTTPS=true
APP_KEYPATH=/absolute/path/to/ddfr.local+2-key.pem
APP_CERTPATH=/absolute/path/to/ddfr.local+2.pem
```

Start the backend with the `https` flag:
```bash
python app/main.py https
```

### Option B — React dev server HTTPS (frontend only)

Create `frontend/.env.development.local` from the template:
```bash
cp frontend/.env.development.local.txt frontend/.env.development.local
```

Fill in the values:
```env
HTTPS=true
SSL_KEY_FILE=/absolute/path/to/key.pem
SSL_CRT_FILE=/absolute/path/to/cert.pem
HOST=ddfr.local
PORT=3000
REACT_APP_WS_PROTOCOL=wss
REACT_APP_WS_HOST=ddfr.local
REACT_APP_WS_PORT=8000
```

Then run `npm start` as usual.

> Both options A and B must be active together for a fully secured setup: the browser must reach the frontend over HTTPS and the WebSocket over WSS.

---

## Local Development

### Prerequisites

- Python 3.11
- Node.js 18+
- MongoDB running locally

### Backend

```bash
cd backend

# Run the hardware-aware setup script (creates .venv and installs deps)
# Windows:
setup.bat
# Linux / macOS:
chmod +x setup.sh && ./setup.sh

# Activate the virtualenv
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows

# Copy and configure the env file
cp example.env.txt app/.env
# Edit app/.env — set DB_URL, DB_NAME, DB_COLLECTION at minimum

# Start the server
python app/main.py
# or with HTTPS:
python app/main.py https
```

### Frontend

```bash
cd frontend
npm install

# Optional: copy the env template if you need custom host/port/protocol
cp .env.development.local.txt .env.development.local
# Edit .env.development.local if needed

npm start
```

The setup scripts detect your hardware (NVIDIA GPU, Apple Silicon, Windows DirectML, or CPU) and install the appropriate ONNX Runtime and FAISS variant automatically.

---

## Contributing

The core recognition pipeline is complete. We are looking for:

- **Testers** — verify installation scripts and WebSocket stability across different environments and hardware
- **Code reviewers** — architecture, best practices, edge cases, security

Please open an issue before submitting a pull request.

---

## License

Distributed under the **GPLv3** license. See [`LICENSE`](LICENSE) for details.
