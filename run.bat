@echo off
REM Startet den Fab Agon Emulator (GUI) mit dem Projekt-Ordner "sdcard" als SD-Karte.
REM Weitere Optionen anhaengbar, z.B.:  run.bat --fullscreen
setlocal
set "ROOT=%~dp0"
set "EMU=%ROOT%tools\fab-agon-emulator-v1.2.4-windows-x64"
cd /d "%EMU%"
"%EMU%\fab-agon-emulator.exe" --sdcard "%ROOT%sdcard" %*
