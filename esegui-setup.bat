@echo off
REM Wrapper per eseguire setup.bat e mantenere la finestra aperta

cd /d "%~dp0"

echo Esecuzione setup.bat...
echo.
echo ========================================
echo IMPORTANTE: Non chiudere questa finestra!
echo ========================================
echo.

call setup.bat

REM Se lo script termina, mantieni la finestra aperta
if errorlevel 1 (
    echo.
    echo ========================================
    echo Lo script e' terminato con errori.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Setup completato con successo!
    echo ========================================
)

echo.
echo Premi un tasto per chiudere questa finestra...
pause >nul

