@echo off
REM Startet den Fab Agon Emulator (GUI) mit dem Projekt-Ordner "sdcard" als SD-Karte.
REM Weitere Optionen anhaengbar, z.B.:  run.bat --fullscreen
setlocal
set "ROOT=%~dp0"
set "EMU=%ROOT%tools\fab-agon-emulator-v1.2.4-windows-x64"
cd /d "%EMU%"
REM --firmware console8 = MOS 2.3.3, dieselbe Firmware wie der CLI-Emulator.
REM Ohne die Option nimmt der GUI-Emulator "platform", das autoexec.txt
REM anders behandelt und eine andere Speicheraufteilung hat.
"%EMU%\fab-agon-emulator.exe" --firmware console8 --sdcard "%ROOT%sdcard" %*
