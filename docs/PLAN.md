# LED-Wand am Agon Light 2 — Projektplan

12×12-Matrix aus SK6812 RGBNW (12 V), angesteuert per GPIO vom Agon Light 2,
programmiert in BBC BASIC.

## 1. Ausgangslage

| | |
|---|---|
| Matrix | 144 Pixel (12×12), SK6812 RGBNW, 12 V, Gehäuse nach [LumaNode](https://www.kickstarter.com/projects/printableaccessories/lumanode) |
| Rechner | Agon Light 2 (Olimex), eZ80 @ 18,432 MHz, MOS 2.3.3 |
| Sprache | BBC BASIC (ADL, `/bin/bbcbasic24`) + eZ80-Assembler für die Bitausgabe |
| Stromversorgung | extern, nur Masse und Datenleitung gehen zum Agon |

### eZ80-GPIO-Register

| Port | DR | DDR | ALT1 | ALT2 |
|---|---|---|---|---|
| B | `&9A` | `&9B` | `&9C` | `&9D` |
| C | `&9E` | `&9F` | `&A0` | `&A1` |
| D | `&A2` | `&A3` | `&A4` | `&A5` |

Zugriff über `OUT (C),A` mit der 16-Bit-I/O-Adresse in `BC` — das sind Standard-Z80-Befehle,
der Inline-Assembler von BBC BASIC genügt also im Prinzip. Pin als Ausgang: Bit im `DDR` auf 0.

### Pinbelegung (34-Pin-Header, Agon Light 2)

Frei nutzbar sind `PC0`–`PC7` (Pins 17–24) und `PD4`–`PD7` (Pins 13–16).
`PC0`–`PC3` haben Zweitfunktionen als UART1 und bleiben deshalb frei.

| Signal | Pin |
|---|---|
| **Daten zur Matrix** | **21 (`PC4`)** |
| GND | 3, 5 oder 33 |
| +5 V (für Pegelwandler) | 4 |
| +3,3 V | 34 |
| SPI MOSI / SCK (Plan B) | 32 / 31 |

## 2. Timing — warum BASIC allein nicht reicht

SK6812 erwartet pro Bit 1,25 µs bei ±150 ns Toleranz. Ein eZ80-Takt dauert 54 ns:

| | Soll | in Takten |
|---|---|---|
| Bitperiode | 1,25 µs | 23 |
| „0" High-Phase | 0,3 µs | 5,5 |
| „1" High-Phase | 0,6 µs | 11 |
| Toleranz | ±150 ns | ±2,8 |
| Reset (Latch) | > 80 µs | — |

Ein BASIC-Interpreter braucht dafür das Hundertfache. Die Bitausgabe muss in Assembler
laufen, BASIC liefert nur den Framebuffer.

Ein vollständiger Frame umfasst 144 × 32 = 4608 Bits, also **5,76 ms** — die ganze Zeit
mit gesperrten Interrupts. Daraus folgen realistisch 20–30 fps.

## 3. Architektur

```
BASIC   Animation, Effekte, Mapping, Helligkeitsbegrenzung
   |
   |    Framebuffer: 144 × 4 Byte GRBW = 576 Byte, in LED-Reihenfolge
   v
Renderer-Schicht  (austauschbar)
   |
   +-- VDP-Backend    Bildschirmvorschau, für Entwicklung ohne Hardware
   +-- GPIO-Backend   Assembler-Bitbang auf PC4      (Plan A)
   +-- SPI-Backend    Hardware-getaktet über MOSI    (Plan B)
```

Der Framebuffer liegt bereits in der Reihenfolge, in der die Bytes auf den Draht gehen
(GRBW pro LED, LED 0 zuerst). Die Ausgaberoutine schiebt ihn dadurch nur noch linear hinaus.

## 4. Plan B — SPI statt Bit-Banging

Falls das Bit-Banging auf echter Hardware am Interrupt-Jitter scheitert: Der eZ80F92 hat
einen SPI-Controller, `MOSI` liegt auf Pin 32. Jedes LED-Bit wird als vier SPI-Bits kodiert,
womit die SPI-Hardware das Timing selbst erzeugt — **immun gegen Interrupts**.

Mit BRG = 3 ergibt sich 18,432 MHz / (2 × 3) = 3,072 MHz, also 325 ns je SPI-Bit:

| LED-Bit | SPI-Muster | High-Zeit | Soll |
|---|---|---|---|
| 0 | `1000` | 325 ns | 300 ± 150 ns ✓ |
| 1 | `1100` | 651 ns | 600 ± 150 ns ✓ |

Beides liegt mittig in der Toleranz. Kosten: 2304 Byte Sendepuffer statt 576, und der
SPI-Bus wird mit der SD-Karte geteilt — während MOS auf die Karte zugreift, sehen die LEDs
Datenmüll. Solange die Animation im RAM läuft, spielt das keine Rolle; nach einem
Dateizugriff genügt ein erneutes Senden des Frames.

Plan C, falls beides scheitert: UART1 (Pins 17/18) zu einem Mikrocontroller, der die LEDs
treibt. Robust, aber kein reines GPIO mehr.

## 5. Hardware-Aufbau

```
Agon Pin 21 (PC4) --> [74AHCT125] --> 330 Ohm --> DIN Matrix
Agon Pin  4 (+5V) --> VCC 74AHCT125
Agon Pin  3 (GND) --> GND --+-- GND Netzteil
                            +-- GND Matrix
12-V-Netzteil ------------------> +12V Matrix
```

- Der Agon gibt 3,3 V aus, SK6812 erwarten am Dateneingang typisch 0,7 × VDD.
  Der **74AHCT125** hebt auf 5 V — ohne ihn ist der Betrieb ein Wackelkandidat.
- **330 Ω** in der Datenleitung dämpft Reflexionen.
- **1000 µF** über +12 V/GND direkt an der Matrix gegen Einschaltspitzen.
- Die **gemeinsame Masse ist nicht optional** — ohne sie hat das Datensignal keinen Bezug.

Bei 144 Pixeln auf Vollweiß summiert sich der Strom erheblich. Deshalb ist im Renderer von
Anfang an ein globaler Helligkeitsfaktor vorgesehen.

## 6. Das LED-Mapping

Kernstück: eine Tabelle `mp%(x,y) -> LED-Index` mit 144 Einträgen statt einer festen Formel.
Sie deckt jede Verdrahtung ab, auch eine fehlerhafte, und kostet zur Laufzeit nur einen
Array-Zugriff.

Erzeugt wird sie aus vier Parametern: Startecke, Serpentine ja/nein, zeilen- oder
spaltenweise, Rotation. Der bei Streifenaufbauten übliche Serpentinenfall:

```basic
IF (y AND 1) = 0 THEN i% = y*12 + x ELSE i% = y*12 + (11-x)
```

Die tatsächliche Topologie geht aus dem LumaNode-Bauplan nicht hervor — das Projekt liefert
nur STL-Dateien und geht von Arduino/FastLED aus. Deshalb gehört ein **Kalibrierprogramm**
dazu (M1): Es zündet LED 0, 1, 2 … einzeln, die Position wird eingegeben, das Ergebnis
landet als `matrix.map` auf der SD-Karte und wird von allen Programmen geladen.

## 7. Meilensteine

| | Inhalt | Hardware nötig |
|---|---|---|
| **M0** ✓ | Framebuffer, Mapping-Tabelle, Renderer-Schicht, VDP-Bildschirmvorschau | nein |
| **M1** | Kalibrierprogramm, `matrix.map` laden/speichern | Matrix |
| **M2** ~ | Assembler-Ausgaberoutine geschrieben und eingebunden; Timing noch offen | alles |
| **M3** | Integration, erste Animation auf der Wand | alles |
| **M4** | Effektbibliothek: Lauflicht, Plasma, Text-Scroller, Bilder von SD | alles |

M0 und M1 sind vollständig ohne angeschlossene Hardware entwickelbar.

## 8. Risiken

**M2 ist der kritische Punkt.** Ob Bit-Test, Ausgabe und Schleifenlogik in 23 Takte passen,
entscheidet sich erst beim Auszählen; vermutlich muss die Schleife pro Byte ausgerollt
werden. Greift sonst Plan B.

**Inline-Assembler im ADL-Modus.** `bbcbasic24` läuft in ADL, dokumentiert ist für den
Inline-Assembler aber nur 8-Bit-Z80. Falls das kollidiert, bauen wir die Routine mit
`/bin/ez80asm` (liegt auf der SD-Karte) als eigenes `.bin` und laden sie per `*LOAD`.

**Emulator-Grenzen.** Der Fab Agon Emulator bildet weder GPIO-Timing noch LEDs ab. M2 und
M3 lassen sich nur auf echter Hardware verifizieren, idealerweise mit Logikanalysator.

## 9. Gemessene Performance (aus M0)

Im Emulator gemessen, `PROCrendervdp` über alle 144 Zellen:

| | Zeit |
|---|---|
| Vollbild, alle Zellen geändert | 90 cs |
| Vollbild, eine Zelle geändert | 66 cs |
| davon reines Zeichnen (144 Zellen) | ~24 cs |

Der Löwenanteil ist also **nicht** die VDU-Ausgabe, sondern der Interpreter selbst: die
Schleife über 144 Pixel mit Array-Zugriff und Farbberechnung kostet allein 0,66 s. Lookup-
Tabellen statt Multiplikation/Division brachten 27 %, mehr ist ohne Assembler nicht drin.

**Daraus folgt: BBC BASIC schafft grob 200–250 Pixeloperationen pro Sekunde.** Ein
Vollbild-Effekt über alle 144 Pixel liegt damit bei etwa 1–2 fps — unabhängig davon, wie
schnell die Ausgabe an die LEDs ist.

Konsequenz für M4: Flüssige Vollbildanimationen brauchen entweder Assembler auch für die
Effektberechnung, oder die Effekte müssen so gebaut werden, dass pro Frame nur wenige Pixel
neu berechnet werden. Für viele LED-Effekte (Lauflicht, langsame Verläufe, Uhren) reicht
die BASIC-Geschwindigkeit dagegen problemlos.

Der reine Rechenanteil ist CPU-gebunden und damit auf echte Hardware übertragbar; der
Zeichenanteil kann dort abweichen, weil der Emulator einen vereinfachten VDP verwendet.

## 10. Vorschau-Rendering (M0, Details)

- **MODE 8** — 320×240, 64 Farben. Optional MODE 136 (identisch, doppelt gepuffert).
- Physische Farben sind 6-Bit `RRGGBB`, der Index ergibt sich also aus
  `(r DIV 64)*16 + (g DIV 64)*4 + (b DIV 64)`.
- Der Weißkanal wird für die Vorschau additiv eingerechnet.
- Gezeichnet wird mit `MOVE x1,y1 : PLOT 101,x2,y2` (gefülltes Rechteck, absolut).
- Zellraster 80 × 85 logische Einheiten ergibt physisch quadratische 20 × 20 Pixel.

## 11. Stand M2 — Assembler-Ausgaberoutine

Umgesetzt in `sdcard/progs/ws2812.asm`, übersetzt mit dem Assembler von der SD-Karte:

```
/bin/ez80asm ws2812.asm ws2812.bin -oB0000 -a1
```

### Zyklen laut eZ80 User Manual UM0077

| Befehl | Takte | | Befehl | Takte |
|---|---|---|---|---|
| `nop` | 1 | | `ld r,n` | 2 |
| `out (bc),r` | 3 | | `ld r,(hl)` | 2 |
| `inc rr` / `dec rr` | 1 | | `xor r` / `or r` | 1 |
| `jr cc,d` | 3 genommen / 2 sonst | | `jr d` | 3 |

### Aufbau

Statt zur Laufzeit Bits zu schieben, entpackt die Routine den Framebuffer zuerst in
einen Bitpuffer: ein Byte je Datenbit, das bereits das fertige Portmuster (`$10` oder
`$00`) enthält. Das kostet den achtfachen Speicher — bei 512 KiB belanglos — und macht
die zeitkritische Schleife so kurz, dass sie exakt aufgeht:

```
ld a,$10 | out (c),a | ld a,(hl) | inc hl | out (c),a | nop nop
xor a    | out (c),a | dec de    | ld a,d | or e      | jr nz
   2          3           2          1         3        1 1 1 1 1 3   = 23 Takte
```

Die vier Befehle der Schleifensteuerung brauchen zusammen genau die sechs Takte, die sonst
mit NOPs zu füllen wären. Die Ausgabe läuft dadurch völlig gleichmäßig — es gibt keine
Naht zwischen Bytes.

| | Takte | Zeit | Sollwert |
|---|---|---|---|
| T0H | 6 | 325 ns | 300 ± 150 ns |
| T1H | 12 | 651 ns | 600 ± 150 ns |
| Periode | 23 | 1248 ns | 1250 ns |

Die erzeugten Opcodes wurden gegen die Rechnung geprüft:
`3E 10 | ED 79 | 7E | 23 | ED 79 | 00 00 | AF | ED 79 | 1B | 7A | B3 | 20 EE` —
18 Byte, Rücksprung exakt auf den Schleifenanfang.

### Speicherlage

BBC BASIC lässt `HIMEM` (`&B0000`) **nicht absenken** — der Versuch endet mit „No room".
Damit bleibt nur der Bereich ab `&B0000`, den MOS für von SD geladene Star-Command-
Programme vorhält. Solange im Betrieb kein Moslet aus `/mos/` startet, bleibt der Code
unangetastet; `PROCsendgpio` prüft vor jedem Frame auf `$C3` und lädt sonst nach.

Nebenbei: `*LOAD` verlangt Hexadezimalzahlen **mit `&`-Präfix** (`*LOAD ws2812.bin &B0000`).
Ohne Präfix wird dezimal interpretiert und stillschweigend nichts geladen.

### Was verifiziert ist — und was nicht

Verifiziert im Emulator: Übersetzung, Opcodes gegen die Zyklenrechnung, Laden nach
`&B0000`, `CALL` beider Einsprungpunkte ohne Absturz, vollständiger Durchlauf aus BASIC
über das Renderer-Backend.

**Nicht verifizierbar ist das Timing selbst.** Ein Kalibriertest (`cyctest.asm`) mit zwei
Schleifen, die sich laut Manual um Faktor drei unterscheiden müssten (6 gegen 17 Takte),
lieferte im Emulator **identische Laufzeiten**. Der Fab Agon Emulator zählt also keine
echten Instruktionszyklen. Damit sind auch die dort gemessenen Frame-Zeiten bedeutungslos
für die reale Hardware.

Die Auslegung nach den Manual-Zyklen ist das Beste, was ohne Gerät möglich ist. Die
Verifikation muss an der echten Wand erfolgen — idealerweise mit Logikanalysator, sonst
über `ledtest.bas`: Zeigt Test 3 statt schwachem Weiß bunte Farben, stimmt das Timing
nicht. Anzupassen ist dann ausschließlich die Anzahl der NOPs zwischen den `out`-Befehlen;
die Struktur bleibt.

Bleibt das Timing instabil, greift Plan B aus Abschnitt 4: Bei SPI erzeugt die Hardware
das Bitmuster, unabhängig von Instruktionszeiten und Wartezyklen.

## Quellen

- [Agon GPIO-Dokumentation](https://agonplatform.github.io/agon-docs/GPIO/)
- [eZ80-GPIO aus Assembler](https://mikolajczyk.org/posts/agon_simple_gpio/) — Registertabelle
- [eZ80F92 Datenblatt](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf) — SPI, Timer, GPIO
- [AgonLight2 Schaltplan](https://github.com/OLIMEX/AgonLight2)
- Lokal: `sdcard/docs/VDP---Screen-Modes.md`, `VDP---PLOT-Commands.md`, `VDP---VDU-Commands.md`
