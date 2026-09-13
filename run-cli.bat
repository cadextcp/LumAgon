@echo off
REM Startet den Emulator headless im Terminal (nur Text, keine Grafik).
REM Praktisch fuer schnelle Tests. Grafikmodi (MODE) funktionieren hier NICHT.
setlocal
set "ROOT=%~dp0"
set "EMU=%ROOT%tools\fab-agon-emulator-v1.2.4-windows-x64"
cd /d "%EMU%"
"%EMU%\agon-cli-emulator.exe" --sdcard "%ROOT%sdcard" %*
