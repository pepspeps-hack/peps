@echo off
REM Dit script start de Torrent Downloader GUI.
REM Zorg ervoor dat Python is geïnstalleerd en toegevoegd aan PATH.
REM Zorg ervoor dat libtorrent is geïnstalleerd (pip install libtorrent).
REM Dit script verwacht dat gui.py in dezelfde map staat.

echo Starting Torrent Downloader GUI...
cd /D "%~dp0"
python gui.py

REM Als het venster meteen sluit na een error, kun je de volgende regel uncommenten (verwijder REM)
REM PAUSE
