# LED-Wand am Agon Light 2 — Projektplan

Lumanode-Wand mit 12×12 Pixeln aus SK6812 RGBNW (12 V), **2 LEDs je Pixel = 288 LEDs**,
angesteuert per GPIO vom Agon Light 2, programmiert in BBC BASIC.

## 0. Stand

Alles liegt in `sdcard/progs/`:

| Datei | Zweck | Stand |
|---|---|---|
| `start.bas` | Startprogramm ohne Bildschirm: Menü per Taste, Rückmeldung mit Tönen | auf dem Agon geprüft |
| `ledmatrix.bas` | Hauptprogramm: Framebuffer, Mapping, Vorschau, Demos, GPIO-Ausgabe | läuft, Grafik ungeprüft |
| `calib.bas` | Kalibrierung bzw. Prüfung der Verdrahtung, schreibt `matrix.map` | Logik verifiziert |
| `ledtest.bas` | Minimalprogramm für die erste Inbetriebnahme, ohne Grafik | läuft |
| `ws2812.asm` | zeitkritische Bitausgabe auf PC4 mit Pixelverdopplung und Helligkeitsbremse | Entpacken verifiziert, Timing ungeprüft |
| `wstest.bas` | Selbsttest für `ws2812.bin`: Entpacken, Verdopplung, Helligkeit | alles OK |
| `matrix.map` | Verdrahtung der Lumanode-Wand, erzeugt von `scripts/gen_lumanode_map.py` | geprüft |
| `scripts/agonmon.py` | Terminal über USB (Konsolenmodus des VDP) | Weg auf dem Agon geprüft, Skript selbst nicht interaktiv |
| `scripts/agonload.py` | Datei per USB auf die SD-Karte im Agon (hexload, CRC-geprüft) | auf dem Agon geprüft |
| `cyctest.asm` | Messhilfe für Instruktionszyklen | zeigte: Emulator taugt dafür nicht |

**Fertig und verifiziert:** Framebuffer und Mapping (M0), Kalibrierverfahren mit allen
16 Verdrahtungen (M1), Übersetzung und Ablauf der Assemblerroutine (M2), Abgleich mit dem
Lumanode-Projekt: 288 LEDs, echte Verdrahtung, Strombremse (Abschnitt 14). Betrieb ohne
Bildschirm mit Autostart, Tönen und Konsole über USB, auf dem Agon geprüft (Abschnitt 15).
Drei MOS-Versionen geprüft (Abschnitt 13). Dateien gehen per USB auf die Karte im Agon
(Abschnitt 16).

**Offen — braucht Hardware:**

1. **Das SK6812-Timing.** Rechnerisch geht es auf, gemessen ist es nicht. Der Emulator
   zählt keine echten Zyklen, kann es also nicht beantworten (Abschnitt 11).
2. **Tastenverlust während der LED-Ausgabe** — gemessen, nicht gelöst (Abschnitt 8).
3. **Die Bildschirmvorschau** wurde nie angesehen — nur geprüft, dass sie fehlerfrei
   durchläuft und die Farbwerte stimmen.
4. **M3 und M4** (Integration an der Wand, Effektbibliothek).

**Nächster Schritt:** Pegelwandler nach Abschnitt 5 aufbauen, den Arduino von der
Datenleitung trennen, das Testmodul anschließen und im Menü von `start.bas` (Abschnitt 15)
eine Taste drücken. Zeigt Schritt 6 des LED-Tests statt schwachem Weiß bunte Farben, stimmt
das Timing nicht — dann sind die NOPs in `ws2812.asm` anzupassen oder Plan B (SPI,
Abschnitt 4) zu ziehen. Vorher das bekannte
defekte Modul reparieren (Abschnitt 5), sonst ist ein Timingfehler nicht von dessen
Aussetzern zu unterscheiden.

## 1. Ausgangslage

| | |
|---|---|
| Matrix | 144 Pixel (12×12) aus 36 Modulen à 2×2 Pixel, **2 LEDs je Pixel = 288 LEDs**, SK6812 RGBNW, 12 V, Gehäuse nach [LumaNode](https://www.kickstarter.com/projects/printableaccessories/lumanode) |
| Bisher | Arduino UNO R4 WiFi mit eigener Firmware (Projekt `lumanode`, `build_lumanode_ha.py`), Daten an Pin 13. Daraus stammen Verdrahtung und Helligkeitsgrenze. |
| Rechner | Agon Light 2 (Olimex), eZ80 @ 18,432 MHz; auf dem Gerät Agon Platform MOS 3 (Arthur), im Emulator MOS 2.3.3 |
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

Belegt durch MOS: PB1 (VBLANK-Interrupt, 50 Hz), PB2–PB7 (SPI, SD-Karte an PB4),
PD0–PD3 (UART0 zum VDP, 1.152.000 Baud, RTS/CTS). Quelle: MOS-Quellcode
(`equs.inc`, `interrupts.asm`, `spi.asm`, `uart.c`).

### Pinbelegung (34-Pin-Header, Agon Light 2)

Frei nutzbar sind `PC0`–`PC7` (Pins 17–24) und `PD4`–`PD7` (Pins 13–16).
`PC0`–`PC3` haben Zweitfunktionen als UART1 und bleiben deshalb frei.

| Signal | Pin |
|---|---|
| **Daten zur Matrix** | **21 (`PC4`)** |
| GND | 3, 5 oder 33 |
| +5 V (für Pegelwandler) | 4 — laut Olimex bis 1,8 A frei, per LiPo-USV gepuffert |
| +3,3 V | 34 |
| SPI MOSI / SCK (Plan B) | 32 / 31 |

**Alle GPIOs arbeiten mit 3,3 V und sind nicht 5-V-tolerant** — laut Olimex-Handbuch
beschädigt ein 5-V-Signal das Board.

## 2. Timing — warum BASIC allein nicht reicht

SK6812 erwartet pro Bit 1,25 µs bei ±150 ns Toleranz. Ein eZ80-Takt dauert 54 ns:

| | Soll | in Takten |
|---|---|---|
| Bitperiode | 1,25 µs | 23 |
| „0" High-Phase | 0,3 µs | 5,5 |
| „1" High-Phase | 0,6 µs | 11 |
| Toleranz | ±150 ns | ±2,8 |
| Reset (Latch) | > 80 µs (neuere WS2812B: > 280 µs) | — |

Ein BASIC-Interpreter braucht dafür das Hundertfache. Die Bitausgabe muss in Assembler
laufen, BASIC liefert nur den Framebuffer.

Ein vollständiger Frame umfasst 288 × 32 = 9216 Bits, also **11,5 ms** — die ganze Zeit
mit gesperrten Interrupts. Die Ausgabe allein schafft damit über 80 fps; die Grenze setzt
BASIC beim Rechnen der Bilder (Abschnitt 9).

## 3. Architektur

```
BASIC   Animation, Effekte, Mapping
   |
   |    Framebuffer: 144 × 4 Byte GRBW = 576 Byte, ein Eintrag je Pixel,
   |    in Kettenreihenfolge der Pixel
   v
Renderer-Schicht  (austauschbar)
   |
   +-- VDP-Backend    Bildschirmvorschau, für Entwicklung ohne Hardware
   +-- GPIO-Backend   Assembler-Bitbang auf PC4      (Plan A)
   |                  sendet jeden Eintrag 2x (2 LEDs je Pixel),
   |                  jedes Byte durch die Helligkeitstabelle (max. 90)
   +-- SPI-Backend    Hardware-getaktet über MOSI    (Plan B)
```

Der Framebuffer liegt bereits in der Reihenfolge, in der die Pixel auf den Draht gehen
(GRBW je Pixel, Pixel 0 zuerst). Die beiden LEDs eines Pixels folgen in der Kette immer
direkt aufeinander, deshalb genügt ein Eintrag je Pixel — die Ausgaberoutine verdoppelt
ihn beim Entpacken (Abschnitt 11).

## 4. Plan B — SPI statt Bit-Banging

Falls das Bit-Banging auf echter Hardware am Interrupt-Jitter scheitert: Der eZ80F92 hat
einen SPI-Controller, `MOSI` liegt auf Pin 32. Jedes LED-Bit wird als vier SPI-Bits kodiert,
womit die SPI-Hardware das Timing selbst erzeugt — **immun gegen Interrupts**.

Mit BRG = 3 (derselbe Teiler, den MOS für die SD-Karte nutzt) ergibt sich
18,432 MHz / (2 × 3) = 3,072 MHz, also 325 ns je SPI-Bit:

| LED-Bit | SPI-Muster | High-Zeit | Soll |
|---|---|---|---|
| 0 | `1000` | 325 ns | 300 ± 150 ns ✓ |
| 1 | `1100` | 651 ns | 600 ± 150 ns ✓ |

Beides liegt mittig in der Toleranz. Der Sendepuffer braucht 288 × 4 × 4 = 4608 Byte.
Der SPI-Bus wird mit der SD-Karte geteilt — ohne Gegenmaßnahme sehen die LEDs bei jedem
Dateizugriff Datenmüll. Abhilfe: Den 74AHCT125 über seinen OE̅-Pin per GPIO nur während
eines LED-Frames durchschalten, dazu 10 kΩ Pull-down an DIN. Ungeklärt ist, ob MOSI
zwischen zwei Bytes low bleibt — das muss vor Plan B gemessen werden.

Plan C, falls beides scheitert: UART1 (Pins 17/18) zu einem Mikrocontroller, der die LEDs
treibt. Robust, aber kein reines GPIO mehr.

## 5. Hardware-Aufbau

```
Agon Pin 4  (+5V) ---------+------------ 14 VCC  74AHCT125
                         100 nF
Agon Pin 3  (GND) ---------+------------  7 GND --+-- GND Netzteil
                                                  +-- GND Matrix
                           GND ---------  1 1OE̅   (Kanal 1 immer an)
Agon Pin 21 (PC4) ----+---------------->  2 1A
                    10 kΩ                 3 1Y --> 330 Ohm --> DIN Matrix
                      |
                     GND                  4, 10, 13 (OE̅ 2-4) -> VCC
                                          5, 9, 12  (A 2-4)   -> GND
12-V-Netzteil ---------------------------------------------> +12V Matrix
```

- Der Agon gibt 3,3 V aus, SK6812 erwarten am Dateneingang typisch 0,7 × VDD.
  Der **74AHCT125** hebt auf 5 V — ohne ihn ist der Betrieb ein Wackelkandidat.
- **Nie** DIN, einen 5-V-Ausgang oder den Arduino direkt an einen Agon-Pin — die GPIOs
  sind nicht 5-V-tolerant. Den 74AHCT125 vom Agon-5-V-Pin versorgen: Dann liegt nie ein
  High an seinem Eingang, während er selbst stromlos ist.
- **100 nF** direkt an VCC/GND des 74AHCT125.
- **10 kΩ Pull-down** an 1A: Nach dem Reset ist PC4 ein Eingang und würde sonst offen
  auf die LEDs rauschen. Beim ersten Einschalten messen: 1A muss unter 0,8 V liegen.
- Unbenutzte Kanäle: OE̅ an VCC (Ausgang hochohmig), Eingänge an GND (nicht offen lassen).
- **330 Ω** in der Datenleitung dämpft Reflexionen.
- **1000 µF** über +12 V/GND direkt an der Matrix gegen Einschaltspitzen.
- Die **gemeinsame Masse ist nicht optional** — ohne sie hat das Datensignal keinen Bezug.
- **Arduino von DIN trennen** (Pin 13): Zwei Treiber auf einer Leitung sind nicht erlaubt.
  *Option:* Kanal 2 des 74AHCT125 für den Arduino nutzen (2A ← Pin 13, 2Y über eigene 330 Ω
  auf denselben DIN-Knoten). Ein Umschalter legt entweder 1OE̅ oder 2OE̅ auf GND, der
  andere hängt über 10 kΩ an VCC. So bleibt die Home-Assistant-Firmware per Schalter
  erreichbar.

### Strombudget

Die Arduino-Firmware begrenzt die Helligkeit auf 120/255 und nutzt den Weißkanal nie —
das ist der im Betrieb erprobte Höchstwert. Hier darf auch W leuchten, deshalb begrenzt
`ws2812.asm` **jeden der vier Kanäle auf 90**: 4 × 90 = 360 entspricht 3 × 120 aus der
Firmware. Die Grenze sitzt in der Assemblerroutine, weil jeder Frame dort durchläuft,
egal welches BASIC-Programm ihn erzeugt. Wer mehr will, misst erst den Strom (max. 3 A
je Einspeisung) und ändert dann `MAXB`.

### Bekannter Defekt

Laut Fehlersuche im Lumanode-Projekt (`debugFreeze.md`) hat das alte Modul 6 — jetzt an
Kettenposition 30 — einen marginalen Ausgang: Bei schnellen, hellen Mustern bricht die
Kette dahinter ab. **Vor der Timing-Prüfung am Agon reparieren**, sonst sieht dessen
Aussetzer aus wie ein Timingfehler.

## 6. Das LED-Mapping

Kernstück: eine Tabelle `mp%(x,y) -> Index` mit 144 Einträgen statt einer festen Formel.
Sie deckt jede Verdrahtung ab, auch eine fehlerhafte, und kostet zur Laufzeit nur einen
Array-Zugriff. Der Index zählt **Pixel in Kettenreihenfolge**; bei der Lumanode-Wand steht
Index k für die LEDs 2k und 2k+1.

**Die Lumanode-Verdrahtung ist bekannt.** Die Arduino-Firmware enthält sie als
`ledPairs[12][12][2]`, übernommen aus dem Pixel-Builder-Plan und am echten Aufbau
korrigiert. Die Kette läuft modulweise in Doppelspalten, in den unteren zwei Modulreihen
der mittleren vier Spalten im Zickzack — keine der 16 Formel-Varianten passt.
`scripts/gen_lumanode_map.py` enthält die Tabelle, prüft sie (jede LED genau einmal, die
zwei LEDs eines Pixels immer benachbart) und schreibt daraus `sdcard/progs/matrix.map`.
Wird die Wand umgebaut, ist dort die Tabelle zu ersetzen und das Skript neu auszuführen.

Die Formel-Varianten und das Kalibrierprogramm (M1) bleiben für andere Aufbauten.
An der Lumanode-Wand dient `calib.bas` zur **Prüfung**: Es lädt `matrix.map` beim Start,
Menüpunkt 3 läuft die Kette ab und zeigt parallel, wo jeder Pixel leuchten muss.

## 7. Meilensteine

| | Inhalt | Hardware nötig |
|---|---|---|
| **M0** ✓ | Framebuffer, Mapping-Tabelle, Renderer-Schicht, VDP-Bildschirmvorschau | nein |
| **M1** ✓ | Kalibrierprogramm, `matrix.map` laden/speichern | Matrix |
| **M2** ~ | Assembler-Ausgaberoutine mit Verdopplung und Helligkeitsbremse; Entpacken verifiziert, Timing offen | alles |
| **L** ✓ | Abgleich mit dem Lumanode-Projekt (Abschnitt 14) | nein |
| **H** ✓ | Betrieb ohne Bildschirm: Autostart, Töne, Konsole über USB (Abschnitt 15) | Agon |
| **M3** | Integration, erste Animation auf der Wand | alles |
| **M4** | Effektbibliothek: Lauflicht, Plasma, Text-Scroller, Bilder von SD | alles |

M0 und M1 sind vollständig ohne angeschlossene Hardware entwickelbar.

## 8. Risiken

**M2 ist der kritische Punkt.** Die Zyklenrechnung geht auf (Abschnitt 11), aber nur
rechnerisch — ob die reale Hardware dieselben Zeiten liefert, ist offen. Wartezyklen beim
Codeabruf aus dem externen RAM oder beim I/O-Zugriff würden alles verschieben. Der Emulator
kann es nicht beantworten. Greift sonst Plan B.

**Tastenverlust während der LED-Ausgabe — gemessen.** Ein Frame sperrt die Interrupts
11,5 ms; UART0 zum VDP (1.152.000 Baud, 16-Byte-FIFO) läuft in dieser Zeit über. Gemessen
auf dem Agon, je 30 Tasten über den Konsolenmodus im Abstand von 0,33 s:

| Lauf | LED-Ausgabe | Töne | RTS vor dem Frame aus | Tasten angekommen |
|---|---|---|---|---|
| A | keine | nein | — | 30 / 30 |
| B | Dauer, 37,8 Frames/s | nein | nein | 24 / 30 |
| C | Dauer | nein | ja | 25 / 30 |
| E | Dauer | nein | ja, Duplex-Flag erneut gesendet | 25 / 30 |
| D | Dauer | Klick je Taste | ja | 21 / 30 |
| Dauertest in `start.bas` | Dauer, ~31 Frames/s | Klick je Taste | nein | 14 / 30 |

- Die Eingabe selbst ist zuverlässig (A); verloren geht nur, was während der Ausgabe ankommt.
- Jede Antwort des VDP belegt denselben FIFO — hier der Status zu jedem Ton. Töne während
  der Dauerausgabe vervielfachen den Verlust.
- RTS zurücknehmen hilft nicht, auch nicht nach erneutem Duplex-Flag
  (`VDU 23,0,&F8,1,1,1,0`, das Platform-MOS beim Start selbst sendet). Der VDP startet laut
  Quelltext im Halbduplex (`HW_FLOWCTRL_RTS`) und beachtet CTS erst im Duplex. Auf diesem
  Gerät wirkt das nicht; ob die installierte VDP-Firmware das Flag kennt, ist offen.
- Gemessen wurde mit Tasten über USB, bei denen der VDP Drücken und Loslassen direkt
  hintereinander schickt. Bei der echten Tastatur liegen beide Pakete rund 100 ms
  auseinander und passen einzeln in den FIFO — der Verlust ist dort vermutlich kleiner.
  Nachzählen im Dauertest: Die Schlusszeile nennt die angekommenen Tasten.

Mögliche Abhilfen, noch nicht umgesetzt: Frames nur senden, wenn sich das Bild ändert;
keine Töne während der Dauerausgabe; wichtige Tasten (ESC, `0`) wiederholen oder halten
(Autorepeat der Tastatur); eine VDP-Firmware mit Duplex-Flusskontrolle; oder den FIFO in
der Low-Phase der Bitschleife leeren und die Bytes nach dem Frame per UART-Loopback an MOS
zurückgeben.

Die VBLANK-Ticks (50 Hz) werden höchstens verzögert; `TIME` über zehn Minuten gegen eine
Uhr prüfen.

*Erledigt:* Die ursprüngliche Sorge, die Schleife müsse pro Byte ausgerollt werden, hat sich
nicht bestätigt — im Gegenteil, das Ausrollen war mit 152 Byte zu weit für einen relativen
Sprung, und die Schleife über einzelne Bits geht exakt auf.

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

### Parameterblock

| Adresse | Inhalt | Vorgabe |
|---|---|---|
| `&B0000` | `jp send` — Frame ausgeben | |
| `&B0004` | `jp gpioinit` — PC4 auf Ausgang | |
| `&B0008` | Adresse Framebuffer (4 Byte) | |
| `&B000C` | Adresse Bitpuffer (4 Byte) | |
| `&B0010` | Anzahl Framebuffer-Bytes (4 Byte) | |
| `&B0014` | LEDs je Eintrag (1 Byte) | 2 |
| `&B0015` | Helligkeit 0–255 (1 Byte) | 255 |

Der Bitpuffer braucht 8 × LEDs-je-Eintrag Byte je Framebuffer-Byte, bei 144 Einträgen
also **9216 Byte** (`DIM bf% np%*64-1`). `*LOAD` setzt die Vorgaben zurück.

### Aufbau

Statt zur Laufzeit Bits zu schieben, entpackt die Routine den Framebuffer zuerst in
einen Bitpuffer: ein Byte je Datenbit, das bereits das fertige Portmuster (`$10` oder
`$00`) enthält. Dabei wird jeder Eintrag zweimal hintereinander entpackt (2 LEDs je Pixel)
und jedes Byte durch eine Helligkeitstabelle geschickt:
`LUT[v] = v × k / 256` mit `k = Helligkeit × 90 / 256`, also höchstens 88. Die Tabelle
liegt bei `&B0800` und wird vor jedem Frame neu gebaut (256 Runden, rund 0,2 ms).

Das kostet Speicher — bei 512 KiB belanglos — und macht die zeitkritische Schleife so
kurz, dass sie exakt aufgeht:

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
18 Byte, Rücksprung exakt auf den Schleifenanfang. Die Schleife selbst ist beim
Lumanode-Abgleich unverändert geblieben.

Die Anzahl der Bits ergibt sich aus dem Ende des Bitpuffers minus Anfang — sie passt damit
immer zu dem, was das Entpacken tatsächlich geschrieben hat.

Nach dem letzten Bit folgt die Latch-Pause: 1000 Runden à 6 Takte = **325 µs**, genug auch
für neuere WS2812B (> 280 µs). Die Interrupts sind dabei schon wieder frei — der Pin ist
low, ein Interrupt kann die Pause nur verlängern.

### Speicherlage

BBC BASIC lässt `HIMEM` (`&B0000`) **nicht absenken** — der Versuch endet mit „No room".
Damit bleibt nur der Bereich ab `&B0000`, den MOS für von SD geladene Star-Command-
Programme vorhält. Solange im Betrieb kein Moslet aus `/mos/` startet, bleibt der Code
unangetastet; `PROCsendgpio` prüft vor jedem Frame auf `$C3` und lädt sonst nach.
Der Code ist 240 Byte groß, die Helligkeitstabelle liegt dahinter bei `&B0800`.

Nebenbei: `*LOAD` verlangt Hexadezimalzahlen **mit `&`-Präfix** (`*LOAD ws2812.bin &B0000`).
Ohne Präfix wird dezimal interpretiert und stillschweigend nichts geladen.

### Was verifiziert ist — und was nicht

Verifiziert im Emulator: Übersetzung, Opcodes gegen die Zyklenrechnung, Laden nach
`&B0000`, `CALL` beider Einsprungpunkte ohne Absturz, vollständiger Durchlauf aus BASIC
über das Renderer-Backend. `wstest.bas` prüft den gesamten Bitpuffer Bit für Bit gegen
die Rechnung:

| Lauf | Ergebnis |
|---|---|
| 2 LEDs je Eintrag, Helligkeit 255 | OK, Höchstwert 88 |
| 2 LEDs je Eintrag, Helligkeit 100 | OK, Höchstwert 34 |
| 1 LED je Eintrag, Helligkeit 255 | OK |
| 2 LEDs je Eintrag, Helligkeit 0 | OK, alles 0 |

In allen Läufen blieb der Speicher hinter dem erwarteten Pufferende unberührt.

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

## 12. Stand M1 — Kalibrierung

`sdcard/progs/calib.bas`, eigenständig und im Textmodus, damit es auch ohne
funktionierende Grafik bedienbar bleibt.

### Kandidatenverfahren

Statt die Topologie aus Messpunkten zu *erraten*, werden alle 16 denkbaren
Verdrahtungen aufgestellt und nacheinander ausgeschlossen:

| Bit | Bedeutung |
|---|---|
| 0 | Serpentine statt progressiv |
| 1 | spaltenweise statt zeilenweise |
| 2 | in x gespiegelt |
| 3 | in y gespiegelt |

Das Programm zündet einzelne LEDs (0, 1, 12, 13, 24), die Position wird im Raster
markiert, und jede Variante, die dazu nicht passt, fällt weg. Sobald nur eine übrig ist,
steht die Verdrahtung fest — meist nach zwei bis drei LEDs.

Der Selbsttest prüft das erschöpfend: Für jede der 16 Verdrahtungen wird geprüft, ob sie
sich aus den Stützstellen wiederfinden lässt. Ergebnis: **alle 16 eindeutig, kein einziger
mehrdeutiger Fall.**

Für Sonderfälle — vertauschte Segmente, Lötfehler, gemischte Laufrichtungen — gibt es
zusätzlich die vollständige Kalibrierung LED für LED.

**Lumanode:** Deren Verdrahtung ist keine der 16 Varianten. Die Schnellkalibrierung meldet
dort erwartungsgemäß „Keine bekannte Verdrahtung passt". `calib.bas` lädt deshalb beim
Start die mitgelieferte `matrix.map` (Abschnitt 6); Menüpunkt 3 prüft sie an der Wand.

### Dateiformat `matrix.map`

| Offset | Inhalt |
|---|---|
| 0 | Breite |
| 1 | Höhe |
| 2 … | je Position ein Byte mit dem Pixel-Index in Kettenreihenfolge, zeilenweise von oben links |

Bei 12×12 also 146 Byte. Bewusst binär statt Text: `BPUT#`/`BGET#` sind in BBC BASIC (Z80)
verlässlich verfügbar, während zeilenweises Text-I/O es nicht ist. Nachvollziehbar bleibt
die Datei über Menüpunkt 6, der die Tabelle anzeigt und prüft, ob jeder Index genau einmal
vorkommt.

`ledmatrix.bas` lädt `matrix.map` beim Start automatisch; die Datei hat Vorrang vor
den eingebauten Formeln und erscheint als Mapping-Stil 3.

### Verifiziert

Kandidatenverfahren für alle 16 Varianten, Schreiben und Lesen der Datei im Rundlauf, und
der Dateiinhalt Byte für Byte gegen die Formel nachgerechnet — null Abweichungen, jeder
Index genau einmal. Die Übernahme in `ledmatrix.bas` wurde mit einer Testkarte geprüft.
Die Lumanode-`matrix.map` wird von beiden Programmen geladen; der Selbsttest von
`ledmatrix.bas` prüft sie mit (Stil 3: jeder Index genau einmal).

Nicht verifizierbar ohne Hardware: ob die Cursortasten die erwarteten Codes 136–139
liefern. Deshalb funktioniert die Rastereingabe alternativ mit **W/A/S/D**.

## 13. Firmware-Kompatibilität

Der Emulator bringt mehrere MOS-Versionen mit. Getestet wurde gegen beide relevanten:

| | Console8 MOS 2.3.3 | Agon Platform MOS 3.0.2 |
|---|---|---|
| `PAGE` / `HIMEM` | `&44E00` / `&B0000` | **identisch** |
| `*LOAD ws2812.bin &B0000` | ✓ | ✓ |
| `CALL &B0004` / `CALL &B0000` | ✓ | ✓ |
| Selbsttest `ledmatrix.bas` | ✓ | ✓ |
| Selbsttest `calib.bas` | ✓ | ✓ |
| BASIC starten | `/bin/bbcbasic24` | `bbcbasic24` |

**Der einzige Unterschied ist der Startbefehl.** MOS 3 hat einen Suchpfad und findet
`bbcbasic24` ohne Pfadangabe; MOS 2.3.3 kennt den nicht und braucht `/bin/`. Umgekehrt
lehnt MOS 3 die Schreibweise mit Pfad als „Invalid command" ab.

Entscheidend für dieses Projekt: **`HIMEM` liegt in beiden Versionen bei `&B0000`**, die
Ladeadresse der Assembler-Routine gilt also für beide.

Die Tests zum Lumanode-Abgleich (Abschnitt 14) liefen unter MOS 2.3.3; `wstest.bas`
besteht zusätzlich unter MOS 3.0.2 und Quark MOS 1.04.

### Folge für `autoexec.txt`

Der direkte Programmaufruf unterscheidet sich, `LOAD` und `RUN` gibt es aber in allen
Versionen. Die mitgelieferte Fassung nutzt diese Form und läuft unverändert unter Quark
MOS 1.04, MOS 2.3.3 und MOS 3.0.2 (Emulator) sowie auf dem echten Agon (MOS 3):

```
SET KEYBOARD 2
VDU 23 0 254 1
cd /progs
LOAD /bin/bbcbasic24.bin
RUN . /progs/start.bas
```

`RUN .` übergibt den Programmnamen an BASIC, das ihn sofort lädt und startet. Schlägt eine
Zeile fehl, bricht MOS die Datei ab; `SET KEYBOARD` und `VDU` brauchen MOS 1.03 oder neuer.

### Emulator-Firmware wählen

`run.bat` legt `--firmware console8` fest, damit das Fenster dieselbe Firmware nutzt wie
der CLI-Emulator, gegen den alles getestet ist. Ohne die Option nähme der GUI-Emulator
`platform`.

Der CLI-Emulator ignoriert `--firmware`, akzeptiert aber `--mos`:

```bash
agon-cli-emulator.exe --mos firmware/mos_platform.bin --sdcard ../../sdcard
```

Damit lassen sich beide Firmwares headless testen.

## 14. Abgleich mit dem Lumanode-Projekt (2026-09-13)

Die Wand hing bisher an einem Arduino mit eigener Firmware (`lumanode/build_lumanode_ha.py`).
Deren Stand wurde gegen dieses Repo gelegt:

| Thema | bisher angenommen | tatsächlich | Änderung |
|---|---|---|---|
| LEDs | 144, eine je Pixel | **288, zwei je Pixel**, in der Kette immer benachbart | `ws2812.asm` sendet jeden Eintrag zweimal; Bitpuffer 9216 Byte |
| Verdrahtung | unbekannt, Serpentine vermutet | bekannt: `ledPairs` der Firmware, Doppelspalten mit Zickzack | `scripts/gen_lumanode_map.py` → `matrix.map`, von beiden Programmen geladen |
| Helligkeit | nur in der Vorschau | Firmware kappt auf 120/255, W = 0 | Helligkeitstabelle in `ws2812.asm`, max. 90 je Kanal |
| Latch | 98 µs | SK6812 > 80 µs, WS2812B > 280 µs | 325 µs, Interrupts dabei schon frei |
| Frame-Dauer | 5,76 ms | 11,5 ms | VDP-Risiko neu bewertet (Abschnitt 8) |
| Farbfolge | GRBW | GRBW (`NEO_GRBW`, 800 kHz) | — |
| Hardware | 74AHCT125, 330 Ω, gemeinsame Masse | dazu Pull-down, 100 nF, Arduino abklemmen, defektes Modul | Abschnitt 5 |

`ledtest.bas` und `calib.bas` rechnen jetzt mit 288 LEDs; die Werte in `ledtest.bas`
sind so gewählt, dass sie nach der Helligkeitsbremse dieselbe Helligkeit ergeben wie
vorher. Geprüft im CLI-Emulator unter MOS 2.3.3: `wstest.bas`, die Selbsttests von
`ledmatrix.bas` und `calib.bas` sowie ein kompletter Durchlauf von `ledtest.bas`.

## 15. Betrieb ohne Bildschirm (2026-09-13)

Der Agon hat keinen Monitor, nur Tastatur und Kopfhörer. Dafür:

- `autoexec.txt` (Abschnitt 13) startet `start.bas` direkt.
- `start.bas` meldet sich über Töne (Audio-API `VDU 23,0,&85`). Aufeinanderfolgende Töne
  laufen abwechselnd auf Kanal 1 und 2: Auf einem Kanal gingen Noten verloren, weil der VDP
  Noten für einen belegten Kanal verwirft und `TIME` nur in 20-ms-Schritten zählt.
  Tonschema und Tasten stehen in der README unter „Betrieb ohne Bildschirm".
- Der Konsolenmodus des VDP (`VDU 23,0,&FE,1`) schickt alle Ausgaben über den USB-Anschluss
  des Agon (CH340, 115200 Baud), und dort gesendete Zeichen kommen als Tastendrücke an.
  Von VDU-Befehlen erscheint nur das Byte 23, die Ausgabe bleibt lesbar.
  `scripts/agonmon.py` ist das Terminal dafür. DTR und RTS bleiben aus, sonst setzt der
  Wandler den ESP32 zurück.

### Auf dem Gerät geprüft

| | Ergebnis |
|---|---|
| Firmware | Agon Platform MOS 3 (Arthur), aus dem Flash gelesen |
| Autostart | `autoexec.txt` → `start.bas`, Konsole aktiv, „Bereit" kommt über USB an |
| Eingabe über USB | Leertaste startet den LED-Test, alle sechs Schritte laufen durch |
| `ws2812.bin` | lädt, jeder Frame kehrt zurück; ohne BASIC-Rechnung 37,8 Frames/s |
| Programm ändern ohne Umstecken | Zeilen über USB eingetippt, `SAVE "/progs/start.bas"`, `RUN` |
| Töne | nach der Kanal-Korrektur alle drei Noten hörbar |
| Tasten während der Ausgabe | gehen teilweise verloren (Abschnitt 8) |

Ob die LEDs richtig leuchten, zeigt erst das angeschlossene Modul — der Datenpin ist
noch nicht gemessen.

Die per `SAVE` geschriebene `start.bas` auf der Karte ist inzwischen per
`scripts/agonload.py` durch die Fassung aus dem Repo ersetzt und am Gerät gegengeprüft
(Abschnitt 16).

## 16. Dateien auf die SD-Karte ohne Umstecken (2026-09-13)

### Über USB — umgesetzt

`scripts/agonload.py DATEI [ZIEL]` schreibt eine beliebige Datei, auch Binärdateien wie
`ws2812.bin`, über den USB-Anschluss auf die Karte im Agon. Grundlage ist `hexload` von
Jeroen Venema: `hexload.bin` liegt in `/mos` der Karte, der VDP bringt den Empfangsteil mit
(`VDU 23,28`). Das Skript baut den PC-Teil (`send.py`) nach und braucht nur `pyserial`.

Ablauf:

1. Agon zum MOS-Prompt: ESC, „Bereit“ abwarten, `0`, „Ende - zurueck zu BASIC“ abwarten,
   `*BYE`, Prompt `/progs *` abwarten. Jeder Schritt wird an der Ausgabe bestätigt.
2. `hexload vdp /progs/agonload.tmp` eintippen. Erst wenn der VDP „Receiving Intel HEX
   records“ meldet, geht das erste HEX-Zeichen hinaus — sonst landete es als Tastendruck im
   Menü von `start.bas`.
3. Intel HEX im erweiterten Format: ein Startsatz mit der CRC32 über alle Daten, jede Zeile
   mit einer CRC16 (Polynom 0x8005, CRC-16/BUYPASS), die der VDP mit seiner eigenen CRC16
   beantwortet. Bei Abweichung geht die Zeile erneut hinaus. Am Ende schickt der VDP die
   CRC32, `hexload` meldet die geschriebenen Bytes.
4. Nur wenn CRC32 und Bytezahl stimmen: das alte Ziel löschen, die temporäre Datei
   umbenennen. `hexload` löscht seine Zieldatei schon vor dem Schreiben, auch bei einem
   Abbruch — eine direkt überschriebene und dann kaputte `ws2812.bin` würde den Autostart
   lahmlegen.
5. BASIC und `start.bas` neu starten.

Die Daten landen ab `&40000` im Speicher, dort läuft BASIC — daher der Weg über den
MOS-Prompt. `hexload` selbst läuft ab `&B0000` und überschreibt die geladene `ws2812.bin`;
`start.bas` lädt sie beim Start neu.

Auf dem Agon geprüft:

| Datei | Größe | Dauer | Prüfung |
|---|---|---|---|
| Testdatei aus Zufallsbytes | 3000 Byte | 2,6 s | CRC32 ok, Prüfsumme per BASIC am Gerät gleich |
| `start.bas` aus dem Repo, ersetzt die vorhandene | 6611 Byte | 5,2 s | CRC32 ok, Prüfsumme gleich, `start.bas` startet |

Gelernt dabei:

- Die VDP-Firmware des Geräts beherrscht das erweiterte Format (antwortet mit „Extended
  mode“ und der CRC16).
- Im Konsolenmodus spiegelt der VDP auch seine eigenen Meldungen („Receiving Intel HEX
  records“, „CRC32 OK“, „VDP done“). Das Skript sucht die CRC-Bytes deshalb im Datenstrom,
  statt genau zwei Bytes zu erwarten.
- `DELETE` einer einzelnen Datei fragt unter MOS 3 nicht nach.
- Tasten gehen verloren, wenn sie ankommen, während BASIC rechnet, und direkt nach ESC in
  `start.bas` — BBC BASIC leert beim Quittieren von Escape den Tastaturpuffer. Befehle erst
  senden, wenn ein Prompt oder eine Meldung da ist; Wartemuster so wählen, dass sie nicht
  schon im Echo der getippten Zeile stehen. Der erste Versuch scheiterte genau daran: Die
  Menüzeile von `start.bas` enthält „0 Ende“ und täuschte das Ende von `start.bas` vor.

Umstecken braucht es nur noch, wenn der Konsolenmodus nicht läuft, etwa nach einer kaputten
`autoexec.txt` — dann `scripts/deploy_sd.py` mit der Karte im Kartenleser.

### Über WLAN — nicht umgesetzt

- Der ESP32 des Agon hat WLAN, die VDP-Firmware nutzt es aber nicht. Eine eigene Firmware
  nur dafür wäre ein großer Umbau neben Bild, Ton und Tastatur — nicht empfohlen.
- Nachrüstbar ist ein ESP8266-Modul am UEXT-Anschluss (etwa Olimex MOD-WIFI-ESP8266) mit
  den Agon-MOS-Tools von nihirash: `Netman` verbindet das Modul mit dem WLAN, der
  Gopher-Browser `Snail` kann laut Beschreibung Dateien aus dem Netz laden. Das ist ein
  Abholen vom Agon aus — auf dem PC bräuchte es einen Gopher-Server —, kein Schieben vom
  PC. Nicht im Detail geprüft.
- Solange der Agon ohnehin per USB am PC hängt, bringt WLAN nichts dazu.

## Quellen

- [Agon GPIO-Dokumentation](https://agonplatform.github.io/agon-docs/GPIO/)
- [eZ80-GPIO aus Assembler](https://mikolajczyk.org/posts/agon_simple_gpio/) — Registertabelle
- [eZ80F92 Datenblatt](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf) — SPI, Timer, GPIO
- [eZ80 CPU User Manual UM0077](https://www.zilog.com/docs/um0077.pdf) — Befehlszyklen
- [AgonLight2 Schaltplan und Handbuch](https://github.com/OLIMEX/AgonLight2) — Pegel, 5-V-Pin, UART-Leitungen
- [Agon MOS Quellcode](https://github.com/AgonPlatform/agon-mos) — Portbelegung durch MOS, Duplex-Flag
- [Agon VDP Quellcode](https://github.com/AgonConsole8/agon-vdp) — Konsolenmodus, 115200 Baud, Flusskontrolle, `hexload.h`
- [agon-hexload](https://github.com/AgonPlatform/agon-hexload) — `hexload.bin`, `send.py`, Übertragungsprotokoll
- [Agon-MOS-Tools](https://github.com/nihirash/Agon-MOS-Tools) — Netman, Snail (ESP8266 am UEXT)
- Lumanode-Projekt: `build_lumanode_ha.py` (Verdrahtung, Helligkeit), `debugFreeze.md` (defektes Modul)
- Lokal: `sdcard/docs/VDP---Screen-Modes.md`, `VDP---PLOT-Commands.md`, `VDP---VDU-Commands.md`
