# Agon Light — BASIC-Entwicklungsumgebung

Arbeitsumgebung für BBC BASIC auf dem Agon Light, komplett lokal und offline lauffähig.

## Schnellstart

1. `run.bat` starten (Doppelklick) → Emulator-Fenster
2. `autoexec.txt` wechselt nach `/progs` und startet BBC BASIC, du landest
   direkt im `>`-Prompt
3. Programm laden und starten:
   ```
   LOAD "ledmatrix.bas"
   RUN
   ```

Zurück ans MOS-Kommandozeile (etwa zum Assemblieren mit `ez80asm`) geht es mit `*BYE`,
von dort mit `/bin/bbcbasic24` wieder in BASIC.

## Ordnerstruktur

| Pfad | Inhalt |
|---|---|
| `run.bat` | Emulator mit Grafik (SDL-Fenster) — der normale Weg |
| `run-cli.bat` | Emulator headless im Terminal — schnelle Texttests, **kein** `MODE`/Grafik |
| `sdcard/` | Die emulierte SD-Karte. Alles hier ist im Emulator sichtbar. |
| `sdcard/progs/` | **Hier kommen eigene Programme hin.** Direkt mit jedem Editor bearbeitbar. |
| `sdcard/bin/` | BBC BASIC + Utilities (Assembler, vi, unzip …) |
| `sdcard/demos/` | Beispielprogramme in BASIC (Cube, Mandelbrot, Sprites, Sound …) |
| `sdcard/games/` | Fertige Spiele zum Ausprobieren |
| `sdcard/docs/` | Komplette Agon-Dokumentation (siehe unten) |
| `sdcard/autoexec.txt` | Wird beim Boot ausgeführt: wechselt nach `/progs` und startet BBC BASIC |
| `tools/` | Fab Agon Emulator v1.2.4 (Windows x64) + heruntergeladenes ZIP |

## Workflow

Der Ordner `sdcard/` ist per `--sdcard` direkt in den Emulator gemountet — es gibt **kein**
Kopieren oder Image-Bauen. Ablauf:

1. `.bas`-Datei in `sdcard/progs/` mit einem beliebigen Editor schreiben
2. Emulator starten (oder, wenn er schon läuft, in BASIC einfach neu `LOAD`en)
3. `LOAD "name.bas"` → `RUN`

Änderungen auf der Platte sind sofort im Emulator sichtbar.

### Format der Quelldateien

- **Klartext** mit **Zeilennummern** — BBC BASIC für Agon lädt Textdateien direkt,
  keine Tokenisierung nötig.
- Zeilenenden: **CRLF** (wie die mitgelieferten Demos).
- `SAVE "name.bas"` aus BASIC heraus schreibt ebenfalls Klartext zurück.

## Die beiden BASIC-Varianten

| Datei | Modus | Speicher | Wann |
|---|---|---|---|
| `/bin/bbcbasic24` | ADL, 24-bit | volle 512 KiB | **Standard** — nimm diesen |
| `/bin/bbcbasic` | Z80, 16-bit | nur 64 KiB | für Code, der Z80-Kompatibilität braucht |

Beide sind BBC BASIC (Z80) Version 3.00 von R.T. Russell, portiert von Dean Belfield.

## Nützliche MOS-Befehle

```
.                    Verzeichnis anzeigen (auch: DIR, *CAT)
cd /progs            Verzeichnis wechseln
/bin/bbcbasic24      BASIC starten
/bin/vi name.bas     Editor auf dem Agon selbst
```

In BASIC leiten MOS-Befehle mit `*` ein, z.B. `*CAT`, `*CD /demos`.

## Dokumentation

Alles liegt lokal in `sdcard/docs/`:

- `BBC-BASIC-for-Agon.md` — Sprachreferenz, Agon-spezifische Erweiterungen
- `VDP---Screen-Modes.md` — alle Bildschirmmodi (Auflösung, Farben)
- `VDP---VDU-Commands.md` — Textausgabe, Cursor, Farben
- `VDP---PLOT-Commands.md` — Linien, Flächen, Kreise
- `VDP---Bitmaps-API.md` / `VDP---Enhanced-Audio-API.md` — Sprites und Sound
- `MOS.md` / `MOS-API.md` — Betriebssystem und Systemaufrufe

## Emulator-Optionen

An `run.bat` durchgereicht, z.B. `run.bat --fullscreen`:

| Option | Wirkung |
|---|---|
| `-f, --fullscreen` | Vollbild |
| `--mode <n>` | in einem bestimmten Bildschirmmodus starten |
| `--scale integer` | pixelgenaue Skalierung statt 4:3 |
| `-u, --unlimited-cpu` | CPU-Takt nicht begrenzen (schnell) |
| `-d, --debugger` | eZ80-Debugger |
| `--firmware quark` | ältere MOS 1.04 Firmware statt MOS 2.3.3 |

Vollständige Liste: `run.bat --help`

## Einrichtung auf einem neuen Rechner

Der Emulator und der SD-Karten-Grundinhalt sind Fremd-Binaries und liegen nicht im Repo
(siehe `.gitignore`). Nach dem Klonen einmalig:

```bash
mkdir -p tools/_downloads
curl -L -o tools/_downloads/fab.zip https://github.com/tomm/fab-agon-emulator/releases/download/1.2.4/fab-agon-emulator-v1.2.4-windows-x64.zip
unzip -q tools/_downloads/fab.zip -d tools/
cp -rn tools/fab-agon-emulator-v1.2.4-windows-x64/sdcard/* sdcard/
```

Danach funktionieren `run.bat` und `run-cli.bat` wie beschrieben. Der eigene Code in
`sdcard/progs/` bleibt dabei unberührt (`cp -n` überschreibt nichts).

## Quellen

- Emulator: [tomm/fab-agon-emulator](https://github.com/tomm/fab-agon-emulator) v1.2.4
- SD-Karten-Inhalt: [tomm/popup-mos](https://github.com/tomm/popup-mos) (im Emulator enthalten)
- BBC BASIC: [breakintoprogram/agon-bbc-basic](https://github.com/breakintoprogram/agon-bbc-basic) v1.06 /
  [-adl](https://github.com/breakintoprogram/agon-bbc-basic-adl) v1.03
