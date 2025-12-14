# DDFR Backend Documentation

Welcome to the official documentation for the DDFR (Face Recognition) Backend API.

## Overview

The DDFR backend is a FastAPI-based application providing face recognition and person management capabilities. It uses MongoDB for data storage, InsightFace for face detection and embedding extraction, and FAISS for efficient similarity search.

## Architecture

The backend is organized into the following modules:

- **Configuration** (`config`): Application settings and environment variables
- **API** (`routers`): REST and WebSocket endpoints
- **Services** (`services`): Core business logic (database, face recognition)
- **Models** (`models`): Data models and schemas
- **Utils** (`utils`): Utility functions and constants

## Quick Start

### Requirements

- **Python 3.11.9** (required - the project is not tested on other versions)
- MongoDB
- Visual C++ Build Tools (Windows) or appropriate build tools (Mac/Linux)
- Required Python packages (installed automatically via setup scripts)

### Installation

**IMPORTANT**: Dependency installation must be done **ONLY** via the provided setup scripts (`setup.bat` for Windows or `setup.sh` for Mac/Linux). Manual installation should only be attempted after carefully reading the requirements files and understanding what is needed for your specific machine configuration.

#### Windows

1. Run the setup script:
```bash
setup.bat
```

This script will:
- Verify Visual C++ Build Tools installation
- Check Python 3.11.9 installation
- Create virtual environment
- Detect hardware (NVIDIA GPU vs CPU/DirectML)
- Install appropriate dependencies from `requirements/universal.txt` or `requirements/nvidia.txt`

#### Mac/Linux

1. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Verify Python 3.11.9 installation
- Detect OS and architecture (Apple Silicon vs Intel, Linux)
- Create virtual environment
- Detect hardware (NVIDIA GPU vs CPU)
- Install appropriate dependencies from `requirements/mac.txt`, `requirements/nvidia.txt`, or `requirements/base.txt`

#### Manual Installation (Advanced)

If you need to install dependencies manually, carefully review the requirements files:
- `requirements/base.txt` - Base dependencies for CPU
- `requirements/nvidia.txt` - Dependencies for NVIDIA GPU support
- `requirements/mac.txt` - Dependencies for macOS (Apple Silicon)
- `requirements/universal.txt` - Universal dependencies for Windows (CPU/DirectML)

**Note**: Manual installation requires understanding which file is appropriate for your system configuration.

#### Configuration

1. Configure environment variables in `.env` file (create in `backend/app/` directory):
```env
DB_URL=mongodb://localhost:27017/
DB_NAME=ddfr_db
DB_COLLECTION=people
DB_HASH="300a31fbdc6f3ff4fb27625c2ed49fdc"
LOG_LOGFOLDER=logs
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
```

See the [Configuration](config/config.md#environment-variables-env) section for a complete list of available environment variables.

2. Activate virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`

3. Run the application:
```bash
cd backend/app
python -m main
```

## Features

- **Face Detection**: Real-time face detection using InsightFace
- **Face Recognition**: Person identification using embedding similarity search
- **Person Management**: CRUD operations for person data
- **WebSocket API**: Real-time face recognition over WebSocket
- **REST API**: Standard HTTP endpoints for data management

## Documentation Structure

Navigate through the documentation using the sidebar to explore:

- Configuration options and settings
- API endpoints and WebSocket connections
- Service implementations and methods
- Data models and validation rules
- Utility functions and constants

