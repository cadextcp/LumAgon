# Agon Light — BASIC-Entwicklungsumgebung

Arbeitsumgebung für BBC BASIC auf dem Agon Light, komplett lokal und offline lauffähig.

## Schnellstart

1. `run.bat` starten (Doppelklick) → Emulator-Fenster
2. `autoexec.txt` schaltet den Konsolenmodus des VDP ein, wechselt nach `/progs` und
   startet darin `start.bas` (Menü mit Tönen, siehe „Betrieb ohne Bildschirm") —
   mit `0` landest du im `>`-Prompt
3. Programm laden und starten:
   ```
   LOAD "ledmatrix.bas"
   RUN
   ```

Zurück ans MOS-Kommandozeile (etwa zum Assemblieren mit `ez80asm`) geht es mit `*BYE`,
von dort mit `/bin/bbcbasic24` wieder in BASIC (auf dem Gerät mit MOS 3: `bbcbasic24` ohne Pfad).

> **Firmware:** `run.bat` startet den Emulator mit `--firmware console8` (MOS 2.3.3),
> derselben Firmware wie der CLI-Emulator. Die `autoexec.txt` lädt BASIC mit `LOAD` und
> `RUN .` und läuft damit unverändert unter Quark MOS 1.04, MOS 2.3.3 und MOS 3.x.
> Auf dem echten Agon läuft Agon Platform MOS 3 („Arthur"). Details in
> [docs/PLAN.md](docs/PLAN.md), Abschnitt 13.

## Ordnerstruktur

| Pfad | Inhalt |
|---|---|
| `run.bat` | Emulator mit Grafik (SDL-Fenster) — der normale Weg |
| `run-cli.bat` | Emulator headless im Terminal — schnelle Texttests, **kein** `MODE`/Grafik |
| `sdcard/` | Die emulierte SD-Karte. Alles hier ist im Emulator sichtbar. |
| `sdcard/progs/` | **Hier kommen eigene Programme hin.** Direkt mit jedem Editor bearbeitbar. |
| `docs/PLAN.md` | Projektplan LED-Wand: Stand, Architektur, Messwerte, offene Punkte |
| `AGENTS.md` | Übergabe für Agenten: Stand, Hardware beim Nutzer, Regeln, Werkzeuge (`CLAUDE.md` verweist darauf) |
| `scripts/` | Hilfsskripte (Python): `emutest.py` und `agonctl.py` steuern Emulator bzw. Agon für Tests, `agonmon.py` ist das Terminal über USB, `agonload.py` schreibt eine Datei per USB auf die Karte im Agon, `deploy_sd.py` spielt den Stand auf die Karte im Kartenleser, `gen_lumanode_map.py` erzeugt `matrix.map` |
| `sdcard/bin/` | BBC BASIC + Utilities (Assembler, vi, unzip …) |
| `sdcard/demos/` | Beispielprogramme in BASIC (Cube, Mandelbrot, Sprites, Sound …) |
| `sdcard/games/` | Fertige Spiele zum Ausprobieren |
| `sdcard/docs/` | Komplette Agon-Dokumentation (siehe unten) |
| `sdcard/autoexec.txt` | Wird beim Boot ausgeführt: deutsche Tastatur, Konsolenmodus, startet `start.bas` |
| `tools/` | Fab Agon Emulator v1.2.4 (Windows x64) + heruntergeladenes ZIP |

## Projekt: LED-Wand

Aktuelles Vorhaben ist die Lumanode-Wand: 12×12 Pixel aus SK6812-RGBNW, **2 LEDs je
Pixel, 288 LEDs**, angesteuert über GPIO. Die Programme liegen in `sdcard/progs/`:

| Datei | Zweck |
|---|---|
| `start.bas` | Startprogramm für den Betrieb ohne Bildschirm: Menü per Taste, Rückmeldung mit Tönen |
| `ledmatrix.bas` | Hauptprogramm mit Vorschau, Demos und LED-Ausgabe |
| `calib.bas` | ermittelt bzw. prüft die Verdrahtung der Matrix |
| `ledtest.bas` | Minimalprogramm für die erste Inbetriebnahme |
| `ws2812.asm` | zeitkritische Bitausgabe mit Pixelverdopplung und Helligkeitsbremse (mit `ez80asm` übersetzen) |
| `wstest.bas` | Selbsttest für `ws2812.bin` im Emulator (Entpacken, nicht Timing) |
| `matrix.map` | Verdrahtung der Lumanode-Wand, erzeugt von `scripts/gen_lumanode_map.py` |

Stand, Architektur und offene Punkte stehen in [docs/PLAN.md](docs/PLAN.md) — Abschnitt 0
gibt die Kurzfassung.

## Betrieb ohne Bildschirm

Der echte Agon läuft ohne Monitor, nur mit Tastatur und Kopfhörer. Beim Einschalten
startet `start.bas` von selbst und meldet sich mit Tönen:

| Ton | Bedeutung |
|---|---|
| aufsteigend C-E-G | bereit, wartet auf eine Taste |
| hoher Doppelpiep | Taste erkannt, es geht los |
| n kurze Pieps | Schritt n des LED-Tests beginnt |
| Klick | nächster Pixel bzw. Taste erkannt (Dauertest) |
| absteigend G-E-C | fertig, abgebrochen oder Ende |
| drei tiefe Töne | Fehler |

Tasten im Menü: `2` Dauertest, `3` LEDs aus, `0` Ende (BASIC-Prompt), jede andere Taste
startet den LED-Test. ESC führt jederzeit zurück ins Menü.

**Über USB mitlesen und tippen:** Hängt der Agon per USB-C am PC, erscheint er als
COM-Port (USB-Seriell-Wandler CH340). `autoexec.txt` schaltet den Konsolenmodus des VDP ein
(`VDU 23 0 254 1`): Alle Ausgaben gehen zusätzlich über USB hinaus, und dort getippte
Tasten kommen beim Agon an wie von der eigenen Tastatur.

```bash
python scripts/agonmon.py
```

Strg+] beendet, braucht `pyserial`. Auf diesem Weg lassen sich auch Programmzeilen
eintippen und mit `SAVE` auf die SD-Karte im Agon schreiben, ohne sie umzustecken.

**Dateien per USB auf die Karte:** `python scripts/agonload.py DATEI [ZIEL]` schreibt eine
beliebige Datei auf die SD-Karte im Agon, auch Binärdateien wie `ws2812.bin` — ohne
Umstecken. `ZIEL` ohne führenden Schrägstrich angeben, etwa `progs/start.bas`. Das Skript
führt den Agon selbst zum MOS-Prompt, überträgt mit `hexload` (CRC-geprüft, erst in eine
temporäre Datei) und startet danach `start.bas` wieder. Details in
[docs/PLAN.md](docs/PLAN.md), Abschnitt 16.

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
/bin/bbcbasic24      BASIC starten (MOS 3: bbcbasic24)
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
