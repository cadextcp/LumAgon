# Übergabe für Agenten

Dieses Repo steuert eine LED-Wand (Lumanode, 12×12 Pixel, 288 SK6812-RGBW-LEDs, 12 V)
direkt von einem **Agon Light 2** aus: BBC BASIC plus eine zeitkritische Routine in
eZ80-Assembler, Daten über GPIO PC4 und einen Pegelwandler SN74AHCT125N.

Lies zuerst **`docs/PLAN.md`, Abschnitt 0** (Kurzfassung, Stand, offene Punkte) und die
**README** (Aufbau des Repos, Emulator, Betrieb ohne Bildschirm).

## Stand (2026-09-13)

- Software fertig und im Emulator geprüft: Framebuffer, Mapping, Pixelverdopplung,
  Helligkeitsbremse, Kalibrierung, Startprogramm mit Tönen (PLAN, Abschnitte 11, 12, 14, 15).
- Auf dem echten Agon geprüft: Autostart, Töne, Konsole über USB, `ws2812.bin` läuft
  (37,8 Frames/s). **Nicht geprüft: ob die LEDs richtig leuchten** — das Timing der
  Bitausgabe ist nur gerechnet. Nächster Schritt: Testmodul anschließen, LED-Test aus
  `start.bas`, Schritt 6 muss schwaches Weiß zeigen (PLAN, Abschnitt 0).
- Bekanntes Problem: Während der LED-Ausgabe gehen Tastendrücke verloren, RTS-Steuerung
  hilft nicht (PLAN, Abschnitt 8, mit Messwerten und Ideen).

## Hardware beim Nutzer

| | |
|---|---|
| Rechner | Agon Light 2 (Olimex), **Agon Platform MOS 3 („Arthur“)**, **kein Monitor** — nur Kopfhörer und Tastatur |
| Verbindung zum PC | USB-C, USB-Seriell-Wandler CH340, bisher **COM7**, 115200 Baud |
| LEDs | vorerst ein einzelnes Testmodul (4 Pixel, 8 LEDs); später die ganze Wand |
| Pegelwandler | SN74AHCT125N, Schaltung in PLAN, Abschnitt 5 |
| Vorher | Arduino UNO R4 WiFi mit eigener Firmware, Ordner `C:\Users\cadex\projekte\lumanode` (kein Git). Dort liegt `build_lumanode_ha.py` mit der Verdrahtungstabelle `ledPairs` und `debugFreeze.md` zum defekten Modul 6 (heute Kettenposition 30). |

Die SD-Karte steckt im Agon. Zum Beschreiben muss der Nutzer sie in den Kartenleser des
PCs stecken (bisher Laufwerk H:) — darum bitten, nicht voraussetzen.

**Inhalt der SD-Karte im Agon (Stand f750f32):** `autoexec.txt` wie im Repo, das
Original des Nutzers als `autoexec.alt` (`SET KEYBOARD 2` / `LOAD bbcbasic.bin` / `RUN`),
`/progs` mit allen Dateien aus `sdcard/progs/`. Die dortige `start.bas` hat BASIC per
`SAVE` geschrieben (Inhalt wie im Repo, Formatierung evtl. anders) — beim nächsten
Umstecken mit `scripts/deploy_sd.py` ersetzen. `/bin` (bbcbasic24, ez80asm) ist identisch
mit dem Emulator. Alles andere auf der Karte gehört dem Nutzer.

## Regeln, die nicht verhandelbar sind

- **Agon-GPIOs sind nicht 5-V-tolerant.** Nie 5 V, DIN oder den Arduino direkt an einen
  Agon-Pin. Nur über den 74AHCT125 (PLAN, Abschnitt 5).
- **Helligkeitsbremse:** `MAXB = 90` in `ws2812.asm` begrenzt jeden Kanal. Nicht erhöhen,
  ohne dass der Nutzer den Strom gemessen hat (max. 3 A je Einspeisung).
- **Flash-Images tabu:** `MOS.bin` und `firmware.bin` auf der SD-Karte nie anfassen,
  keine Firmware flashen.
- **Serieller Port:** DTR und RTS aus lassen (alle Skripte tun das), sonst setzt der
  Wandler den ESP32 zurück und der Konsolenmodus ist weg.
- **Zeilenenden:** `.bas`, `.bat` und `autoexec.txt` brauchen CRLF (BBC BASIC, MOS),
  `matrix.map` ist binär — `.gitattributes` regelt das, beim Schreiben per Skript beachten.

## Werkzeuge

| Aufgabe | Werkzeug |
|---|---|
| Emulator mit Fenster | `run.bat` (Einrichtung: README, „Einrichtung auf einem neuen Rechner“) |
| Emulator ohne Fenster steuern, Tests | `python scripts/emutest.py …` — Beispiele und Eigenheiten im Kopf des Skripts |
| `ws2812.bin` bauen | im Emulator, siehe Beispiel in `scripts/emutest.py` |
| echten Agon steuern und mitlesen | `python scripts/agonctl.py …` — Beispiele im Kopf des Skripts |
| Terminal für den Nutzer | `python scripts/agonmon.py` (Strg+] beendet) |
| Stand auf die SD-Karte | `python scripts/deploy_sd.py H:` (erst `--dry-run`) |
| Verdrahtungstabelle neu | `python scripts/gen_lumanode_map.py` nach Änderung von `ledPairs` |

**Tests im Emulator:**

- `wstest.bas` prüft `ws2812.bin` Bit für Bit (Endmarke `wstest: `).
- `ledmatrix.bas` und `calib.bas`: `LOAD "…" : PROCinit : PROCselftest` (ohne `MODE`, läuft
  im CLI-Emulator).
- Die `autoexec.txt` startet `start.bas`; mit der Taste `0` geht es in den BASIC-Prompt.

**Am Gerät** sieht man nichts — nur, was über USB zurückkommt, und was der Nutzer hört
(Tonschema: README, „Betrieb ohne Bildschirm“). Per `agonctl.py` lassen sich BASIC-Zeilen
eintippen und mit `SAVE` auf die Karte im Agon schreiben; Binärdateien wie `ws2812.bin`
brauchen dagegen das Umstecken der Karte.

## MOS-Unterschiede

Der Emulator läuft standardmäßig mit Console8 MOS 2.3.3, das Gerät mit Platform MOS 3.
Am MOS-Prompt startet BASIC unter MOS 2.3.3 mit `/bin/bbcbasic24`, unter MOS 3 nur mit
`bbcbasic24` (ohne Pfad). `LOAD /bin/bbcbasic24.bin` und `RUN` gehen überall — so macht es
die `autoexec.txt` (PLAN, Abschnitt 13). `HIMEM` liegt überall bei `&B0000`, der Ladeadresse
von `ws2812.bin`.

**Git Bash als Shell:** Argumente, die mit `/` beginnen, wandelt Git Bash in Windows-Pfade
um — eine Eingabe `"/bin/ez80asm …"` an `emutest.py` oder `agonctl.py` kommt verfälscht an.
Deshalb `LOAD /bin/ez80asm.bin` + `RUN . …` verwenden (so in den Beispielen) oder
`MSYS_NO_PATHCONV=1` voranstellen.

## Konventionen

- Dokumentation und Kommentare auf Deutsch. In `.bas`/`.asm` nur ASCII (ae, oe, ue, ss),
  in Markdown echte Umlaute.
- BASIC-Zeilennummern in Zehnerschritten, eingefügte Zeilen dazwischen.
- Commit-Nachrichten auf Deutsch in ASCII, erste Zeile kurz, danach das Warum.
- Messwerte und Entscheidungen gehören in `docs/PLAN.md` — der Plan ist das Gedächtnis
  des Projekts.
