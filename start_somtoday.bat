@echo off
color 0b
echo =========================================
echo       Starten van Somtoday Portaal
echo =========================================
echo.

cd /d "%~dp0\somtoday-api" || cd somtoday-api

:: Controleer of Node.js geinstalleerd is
node -v >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [Fout] Node.js is niet geinstalleerd! Download het via https://nodejs.org/
    pause
    exit
)

:: Controleer of de benodigde bestanden (node_modules) er zijn, installeer anders
IF NOT EXIST "node_modules\" (
    echo [Info] Eerste keer opstarten: pakketten installeren... dit duurt heel even.
    call npm install
    echo [Info] Installatie voltooid!
    echo.
)

:: Controleer of het inlogbestand (.env) bestaat
IF NOT EXIST ".env" (
    echo [Let op!] Je hebt nog geen inloggegevens ingevuld.
    echo Kopieert standaard bestand...
    copy .env.example .env
    echo.
    echo ==========================================================
    echo Ik heb een '.env' bestand voor je aangemaakt in de map.
    echo Open dit bestand (bijv. in Kladblok) en vul je:
    echo 1. SCHOOL
    echo 2. USERNAME (Leerlingnummer)
    echo 3. PASSWORD in.
    echo ==========================================================
    echo.
    echo Sluit dit venster, vul je gegevens in en start dit script daarna opnieuw!
    pause
    exit
)

echo [Succes] Server wordt gestart...
echo Je browser opent zo dadelijk vanzelf.
echo Sluit dit zwarte venster NIET af zolang je de website gebruikt!
echo.

:: Open de browser (werkt in de achtergrond)
start "" http://localhost:3000

:: Start de applicatie expliciet en houd het venster open als er een fout is
call node server.js

echo.
echo [Fout] De server is onverwacht gestopt. Lees de foutmelding hierboven.
pause
