@echo off
setlocal enabledelayedexpansion

REM Imposta encoding UTF-8 per caratteri speciali
chcp 65001 >nul

REM Assicura che lo script operi nella cartella in cui si trova
cd /d "%~dp0"
if errorlevel 1 (
    echo ERRORE: Impossibile accedere alla directory dello script.
    echo Assicurati che il file setup.bat sia in una directory valida.
    pause
    exit /b 1
)

echo ========================================
echo Setup Automatico DDFR - Windows
echo ========================================
echo.

REM --- [1/5] VERIFICA VISUAL C++ BUILD TOOLS ---
echo [1/5] Verifica Visual C++ Build Tools...

set "VC_INSTALLED=0"
set "VC_PATH="

REM -------------------------------------------------------------------------
REM METODO UNICO: VSWHERE.EXE (Metodo Ufficiale Microsoft)
REM -------------------------------------------------------------------------
call :find_vswhere

if not defined VSWHERE_PATH (
    echo.
    echo [ERRORE] vswhere.exe non trovato. Installa i Visual C++ Build Tools:
    echo https://visualstudio.microsoft.com/it/visual-cpp-build-tools/
    pause
    exit /b 1
)

echo Ricerca con vswhere.exe...
for /f "usebackq delims=" %%p in (`"%VSWHERE_PATH%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2^>nul`) do (
    call :check_vs_path "%%p"
)
if "!VC_INSTALLED!"=="0" (
    for /f "usebackq delims=" %%p in (`"%VSWHERE_PATH%" -latest -products * -property installationPath 2^>nul`) do (
        call :check_vs_path "%%p"
    )
)

REM -------------------------------------------------------------------------
REM ESITO CONTROLLO
REM -------------------------------------------------------------------------
if "!VC_INSTALLED!"=="1" goto :vc_ok
if "!VC_INSTALLED!"=="0" (
    echo.
    echo ========================================
    echo [ERRORE CRITICO] Visual C++ Build Tools non trovati!
    echo ========================================
    echo.
    echo Nessuna installazione valida trovata con:
    echo - vswhere.exe (strumento ufficiale Microsoft)
    echo.
    echo Le librerie Python richiedono il compilatore C++ per essere installate.
    echo (insightface, opencv-python, numpy, ecc.)
    echo.
    echo ========================================
    echo ISTRUZIONI INSTALLAZIONE
    echo ========================================
    echo.
    echo OPZIONE 1 - Build Tools Standalone (Raccomandato, ~3GB):
    echo 1. Scarica: https://visualstudio.microsoft.com/it/visual-cpp-build-tools/
    echo 2. Esegui l'installer scaricato
    echo 3. IMPORTANTE: Seleziona il workload "Sviluppo per desktop con C++"
    echo 4. Opzionale: Seleziona anche "Windows 10/11 SDK" (latest)
    echo 5. Clicca "Installa" e attendi il completamento
    echo.
    echo OPZIONE 2 - Visual Studio Community (IDE completo, ~8GB):
    echo 1. Scarica: https://visualstudio.microsoft.com/it/downloads/
    echo 2. Durante l'installazione, seleziona "Sviluppo per desktop con C++"
    echo.
    echo Dopo l'installazione, riprova questo script.
    echo.
    pause
    exit /b 1
)

:vc_ok
if defined VC_PATH (
    echo Visual C++ Build Tools rilevati in: !VC_PATH! ^✓
) else (
    echo Visual C++ Build Tools rilevati ^✓
)
echo.

REM --- [2/5] VERIFICA PYTHON ---
echo [2/5] Verifica installazione Python 3.11.x...

set PYTHON_CMD=
REM Tentativo 1: Py Launcher
py -3.11 --version >nul 2>&1
if not errorlevel 1 ( set "PYTHON_CMD=py -3.11" & goto :check_version )

REM Tentativo 2: Python 3.11 diretto
python3.11 --version >nul 2>&1
if not errorlevel 1 ( set "PYTHON_CMD=python3.11" & goto :check_version )

REM Tentativo 3: Python generico
python --version >nul 2>&1
if not errorlevel 1 ( set "PYTHON_CMD=python" & goto :check_version )

goto :python_not_found

:check_version
for /f "tokens=2 delims= " %%i in ('"%PYTHON_CMD%" --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set FOUND_MAJOR=%%a
    set FOUND_MINOR=%%b
)

if "%FOUND_MAJOR%"=="3" if "%FOUND_MINOR%"=="11" goto :python_ok

echo ERRORE: Trovato Python %PYTHON_VERSION%, ma e' richiesto Python 3.11.x.
goto :python_install_info

:python_not_found
echo ERRORE: Python 3.11 non trovato nel PATH.

:python_install_info
echo.
echo Opzioni:
echo 1. winget install Python.Python.3.11
echo 2. pyenv install 3.11.9 ^&^& pyenv global 3.11.9
pause
exit /b 1

:python_ok
echo Python trovato: %PYTHON_VERSION% ^✓
echo.

REM --- [3/5] CREAZIONE VENV ---
echo [3/5] Gestione Virtual Environment...
if not exist ".venv" (
    echo Creazione nuovo virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERRORE CRITICO: Impossibile creare il venv.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment gia' esistente.
)
echo.

REM --- [4/5] ATTIVAZIONE E AGGIORNAMENTO ---
echo [4/5] Attivazione environment e aggiornamento pip...
if not exist ".venv\Scripts\activate.bat" (
    echo ERRORE: Venv corrotto. Cancella la cartella .venv e riprova.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
echo Pip aggiornato.
echo.

REM --- [5/5] CONFIGURAZIONE AMBIENTE BUILD E INSTALLAZIONE DIPENDENZE ---
echo [5/5] Configurazione ambiente build e installazione dipendenze...

REM Configura l'ambiente build se abbiamo trovato il percorso Visual Studio
REM Questo assicura che pip possa trovare il compilatore C++ durante l'installazione
if defined VC_PATH (
    if exist "!VC_PATH!\VC\Auxiliary\Build\vcvarsall.bat" (
        echo Configurazione ambiente build da: !VC_PATH!
        call "!VC_PATH!\VC\Auxiliary\Build\vcvarsall.bat" x64 >nul 2>&1
        if errorlevel 1 (
            echo [WARNING] Impossibile configurare vcvarsall.bat, continuo comunque...
        ) else (
            echo Ambiente build configurato ^✓
        )
    )
)

echo Rilevamento hardware...

nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [INFO] GPU NVIDIA non rilevata. Uso DirectML/CPU.
    if not exist "requirements\universal.txt" (
        echo ERRORE: requirements\universal.txt mancante!
        pause
        exit /b 1
    )
    pip install -r requirements\universal.txt
) else (
    echo [INFO] GPU NVIDIA rilevata!
    for /f "tokens=* delims=," %%g in ('nvidia-smi --query-gpu^=name --format^=csv^,noheader') do echo Scheda: %%g
    
    if not exist "requirements\nvidia.txt" (
        echo ERRORE: requirements\nvidia.txt mancante!
        pause
        exit /b 1
    )
    pip install -r requirements\nvidia.txt
)

if errorlevel 1 (
    echo.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo ERRORE INSTALLAZIONE DIPENDENZE
    echo Assicurati di aver installato C++ Build Tools e riprova.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completato!
echo ========================================
echo Per attivare: .venv\Scripts\activate
echo.
pause

goto :eof

:check_vs_path
set "CAND=%~1"
if "!VC_INSTALLED!"=="1" exit /b
if "%CAND%"=="" exit /b
if exist "!CAND!\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Trovato percorso valido: "!CAND!"
    set "VC_INSTALLED=1"
    set "VC_PATH=!CAND!"
) else (
    REM no-op
)
exit /b

:check_vs_reg
if "!VC_INSTALLED!"=="1" exit /b
set "REG_KEY=%~1"
set "REG_VER=%~2"
for /f "tokens=3" %%p in ('reg query "%REG_KEY%" /v "%REG_VER%" 2^>nul ^| findstr "%REG_VER%"') do (
    if exist "%%p\VC\Auxiliary\Build\vcvarsall.bat" (
        echo Trovato nel registro %REG_VER%: %%p
        set "VC_INSTALLED=1"
        set "VC_PATH=%%p"
    )
)
exit /b

:find_vswhere
set "VSWHERE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE_PATH%" exit /b
for /f "usebackq delims=" %%q in (`where vswhere 2^>nul`) do (
    set "VSWHERE_PATH=%%q"
    exit /b
)
set "VSWHERE_PATH="
exit /b