@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Setup Automatico DDFR - Windows
echo ========================================
echo.

REM Verifica presenza Python 3.11.14
echo [1/4] Verifica installazione Python 3.11.14...

REM Prova prima python3.11, poi python
set PYTHON_CMD=
python3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python3.11"
    goto :check_version
)
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :check_version
)
echo ERRORE: Python 3.11.14 non trovato.
echo Installare Python 3.11.14 da: https://www.python.org/downloads/release/python-31114/
pause
exit /b 1

:check_version
for /f "tokens=2" %%i in ('"%PYTHON_CMD%" --version 2^>^&1') do set PYTHON_VERSION=%%i
set REQUIRED_VERSION=3.11.14

if not "%PYTHON_VERSION%"=="%REQUIRED_VERSION%" (
    echo ERRORE: Versione Python errata.
    echo Richiesta: %REQUIRED_VERSION%
    echo Trovata: %PYTHON_VERSION%
    echo.
    echo Installare Python 3.11.14 da: https://www.python.org/downloads/release/python-31114/
    pause
    exit /b 1
)

echo Python trovato: %PYTHON_VERSION% ^✓
echo.

REM Crea virtual environment se non esiste
echo [2/4] Creazione virtual environment...
if not exist ".venv" (
    echo Creazione nuovo virtual environment...
    "%PYTHON_CMD%" -m venv .venv
    if errorlevel 1 (
        echo ERRORE: Impossibile creare virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment creato con successo.
) else (
    echo Virtual environment gia' esistente.
)
echo.

REM Attiva virtual environment
echo [3/4] Attivazione virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRORE: Impossibile attivare virtual environment.
    pause
    exit /b 1
)
echo Virtual environment attivato.
echo.

REM Aggiorna pip
echo Aggiornamento pip...
"%PYTHON_CMD%" -m pip install --upgrade pip >nul 2>&1
echo.

REM Verifica presenza GPU NVIDIA
echo [4/4] Rilevamento hardware...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo GPU NVIDIA non rilevata.
    echo Installazione dipendenze per DirectML (AMD/Intel)...
    pip install -r requirements\universal.txt
    if errorlevel 1 (
        echo ERRORE: Installazione dipendenze fallita.
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo Setup completato con DirectML!
    echo ========================================
) else (
    echo GPU NVIDIA rilevata!
    echo Installazione dipendenze per NVIDIA GPU...
    pip install -r requirements\nvidia.txt
    if errorlevel 1 (
        echo ERRORE: Installazione dipendenze fallita.
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo Setup completato con supporto NVIDIA GPU!
    echo ========================================
)

echo.
echo Per attivare il virtual environment in futuro, esegui:
echo   .venv\Scripts\activate.bat
echo.
pause
