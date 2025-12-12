#!/bin/bash

set -e  # Esce in caso di errore

echo "========================================"
echo "Setup Automatico DDFR - Mac/Linux"
echo "========================================"
echo ""

# Verifica presenza Python 3.11.14
echo "[1/5] Verifica installazione Python 3.11.14..."

# Prova prima python3.11, poi python3
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "ERRORE: Python 3.11.14 non trovato."
    echo "Installare Python 3.11.14:"
    echo "Mac: brew install python@3.11"
    echo "Linux: sudo apt-get install python3.11 python3.11-venv"
    echo "Oppure scarica da: https://www.python.org/downloads/release/python-31114/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11.14"

if [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "ERRORE: Versione Python errata."
    echo "Richiesta: $REQUIRED_VERSION"
    echo "Trovata: $PYTHON_VERSION"
    echo ""
    echo "Installare Python 3.11.14:"
    echo "Mac: brew install python@3.11"
    echo "Linux: sudo apt-get install python3.11 python3.11-venv"
    echo "Oppure scarica da: https://www.python.org/downloads/release/python-31114/"
    exit 1
fi

echo "Python trovato: $PYTHON_VERSION ✓"
echo ""

# Rileva OS
echo "[2/5] Rilevamento sistema operativo..."
OS=$(uname -s)
ARCH=$(uname -m)
echo "OS: $OS"
echo "Architettura: $ARCH"
echo ""

# Crea virtual environment se non esiste
echo "[3/5] Creazione virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creazione nuovo virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERRORE: Impossibile creare virtual environment."
        exit 1
    fi
    echo "Virtual environment creato con successo."
else
    echo "Virtual environment già esistente."
fi
echo ""

# Attiva virtual environment
echo "[4/5] Attivazione virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERRORE: Impossibile attivare virtual environment."
    exit 1
fi
echo "Virtual environment attivato."
echo ""

# Aggiorna pip
echo "Aggiornamento pip..."
pip install --upgrade pip > /dev/null 2>&1
echo ""

# Installa dipendenze in base all'OS e hardware
echo "[5/5] Rilevamento hardware e installazione dipendenze..."

if [ "$OS" = "Darwin" ]; then
    # macOS
    if [ "$ARCH" = "arm64" ]; then
        echo "Apple Silicon (M1/M2/M3) rilevato!"
        echo "Installazione dipendenze per Apple Silicon con CoreML..."
        pip install -r requirements/mac.txt
        if [ $? -ne 0 ]; then
            echo "ERRORE: Installazione dipendenze fallita."
            exit 1
        fi
        echo ""
        echo "========================================"
        echo "Setup completato con supporto Apple Silicon!"
        echo "========================================"
    else
        echo "Mac Intel rilevato."
        echo "Installazione dipendenze per CPU..."
        pip install -r requirements/base.txt
        if [ $? -ne 0 ]; then
            echo "ERRORE: Installazione dipendenze fallita."
            exit 1
        fi
        echo ""
        echo "========================================"
        echo "Setup completato per Mac Intel (CPU)!"
        echo "========================================"
    fi
elif [ "$OS" = "Linux" ]; then
    # Linux
    if command -v nvidia-smi &> /dev/null; then
        echo "GPU NVIDIA rilevata!"
        echo "Installazione dipendenze per NVIDIA GPU..."
        pip install -r requirements/nvidia.txt
        if [ $? -ne 0 ]; then
            echo "ERRORE: Installazione dipendenze fallita."
            exit 1
        fi
        echo ""
        echo "========================================"
        echo "Setup completato con supporto NVIDIA GPU!"
        echo "========================================"
    else
        echo "GPU NVIDIA non rilevata."
        echo "Installazione dipendenze per CPU..."
        pip install -r requirements/base.txt
        if [ $? -ne 0 ]; then
            echo "ERRORE: Installazione dipendenze fallita."
            exit 1
        fi
        echo ""
        echo "========================================"
        echo "Setup completato per Linux (CPU)!"
        echo "========================================"
    fi
else
    echo "ERRORE: Sistema operativo non supportato: $OS"
    echo "Installazione dipendenze base (CPU)..."
    pip install -r requirements/base.txt
    if [ $? -ne 0 ]; then
        echo "ERRORE: Installazione dipendenze fallita."
        exit 1
    fi
    echo ""
    echo "========================================"
    echo "Setup completato (configurazione generica)!"
    echo "========================================"
fi

echo ""
echo "Per attivare il virtual environment in futuro, esegui:"
echo "  source .venv/bin/activate"
echo ""
