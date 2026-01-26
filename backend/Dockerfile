# Backend Dockerfile per DDFR
FROM python:3.11.9-slim

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installa dipendenze di sistema necessarie per OpenCV e altre librerie
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia i file requirements
COPY requirements/base.txt requirements/base.txt
COPY requirements/docker.txt requirements/docker.txt

# Installa dipendenze Python
RUN pip install --upgrade pip && \
    pip install -r requirements/docker.txt

# Copia il codice dell'applicazione
COPY app/ ./app/

# Crea directory per logs e immagini
RUN mkdir -p /app/app/logs /app/app/img

# Espone la porta 8000
EXPOSE 8000

# Comando per avviare l'applicazione
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
