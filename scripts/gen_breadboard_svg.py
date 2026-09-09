# -*- coding: utf-8 -*-
"""Erzeugt das Breadboard-Schaubild fuer den Pegelwandler (docs/bilder/).

Draufsicht auf das Breadboard mit SN74AHCT125N, Widerstaenden, Kondensator
und den Anschluessen an Agon, 12-V-Netzteil und LED-Testmodul. Die Geometrie
entspricht docs/AUFBAU-PEGELWANDLER.md: IC in Spalten 20-26, Datenknoten in
Spalte 17, beide Schienenpaare benutzt und am rechten Rand verbunden.

Zeichenregeln (stehen auch in der Legende):
- Verbunden ist nur, wo ein Punkt sitzt. Leitungen ueber Schienen oder
  Loecher ohne Punkt sind dort nicht verbunden.
- Kreuzen sich zwei Leitungen, springt die waagrechte mit einem Bogen ueber
  die senkrechte (hop). Reihenfolge: waagrechte zeichnen, hop(), senkrechte.

Aufruf:  python scripts/gen_breadboard_svg.py  [ausgabedatei]
"""

import os
import sys

W, H = 1400, 850

# ---------------------------------------------------------------- Geometrie


def colx(c):  # Spaltennummer -> x-Position der Lochreihe
    return 240 + (c - 15) * 40


TOP = [228, 250, 272, 294, 316]   # Lochreihen oberhalb der Mittelluecke
BOT = [364, 386, 408, 430, 452]   # Lochreihen unterhalb der Mittelluecke
BOARD = (200, 150, 900, 552)      # x0, y0, x1, y1
RED_T, BLUE_T = 172, 202          # obere Schienen
BLUE_B, RED_B = 500, 530          # untere Schienen
GROOVE = (324, 356)

RED = "#d32f2f"      # +5 V
BLUE = "#1565c0"     # Schienenfarbe GND
BLK = "#212121"      # GND-Leitungen
ORG = "#ef6c00"      # Daten 3,3 V
YEL = "#c89000"      # Daten 5 V
P12 = "#8e24aa"      # 12 V
LEG = "#8d8d8d"      # Bauteil-Beinchen
DOT = "#c9bd97"
BG_BOARD = "#f5f0dc"
BG = "#ffffff"

S = []  # SVG-Elemente


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add(s):
    S.append(s)


def text(x, y, t, size=9, fill="#333", anchor="start", weight="normal", halo=False):
    extra = ' stroke="#f5f0dc" stroke-width="3" paint-order="stroke"' if halo else ""
    add(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{extra}>{esc(t)}</text>')


def wire(points, color, w=3):
    pts = " ".join(f"{x},{y}" for x, y in points)
    add(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')


def hop(x, y, color, bg):
    """Kreuzung ohne Verbindung: Bogen der waagrechten Leitung, genau ueber x zentriert."""
    add(f'<line x1="{x-7}" y1="{y}" x2="{x+7}" y2="{y}" stroke="{bg}" stroke-width="6"/>')
    add(f'<path d="M {x-7} {y} A 7 7 0 0 1 {x+7} {y}" fill="none" stroke="{color}" '
        f'stroke-width="3" stroke-linecap="round"/>')


def plug(x, y, color, r=4.5):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="#333" stroke-width="0.75"/>')


def badge(x, y, num):
    add(f'<circle cx="{x}" cy="{y}" r="8.5" fill="#fff" stroke="#555" stroke-width="1.2"/>')
    text(x, y + 3.3, num, size=9, fill="#111", anchor="middle", weight="bold")


def bands_4(first, second, mult):
    return [first, second, mult]


def resistor_h(cx, y, bands, label):
    """Widerstand waagrecht, Beinchen ausserhalb dieser Funktion zeichnen."""
    add(f'<rect x="{cx-22}" y="{y-6}" width="44" height="12" rx="5" fill="#e8d5a3" '
        f'stroke="#8a7a4a" stroke-width="1"/>')
    for i, b in enumerate(bands):
        add(f'<rect x="{cx-15+i*9}" y="{y-6}" width="4" height="12" fill="{b}"/>')
    add(f'<rect x="{cx+15}" y="{y-6}" width="4" height="12" fill="#c8a23a"/>')
    text(cx, y + 18, label, size=8.5, fill="#555", anchor="middle", halo=True)


def resistor_v(x, cy, bands, label):
    """Widerstand senkrecht, Beschriftung rechts daneben."""
    add(f'<rect x="{x-6}" y="{cy-16}" width="12" height="32" rx="5" fill="#e8d5a3" '
        f'stroke="#8a7a4a" stroke-width="1"/>')
    for i, b in enumerate(bands):
        add(f'<rect x="{x-6}" y="{cy-11+i*6}" width="12" height="3" fill="{b}"/>')
    add(f'<rect x="{x-6}" y="{cy+9}" width="12" height="3" fill="#c8a23a"/>')
    text(x + 11, cy + 3, label, size=8.5, fill="#555", halo=True)


BROWN, BLACK, ORANGE = "#6b3f1d", "#111111", "#ef6c00"
GREY, WHITE, REDB = "#9e9e9e", "#ffffff", "#c62828"

# ---------------------------------------------------------------- Grundgeruest

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

text(560, 40, "Pegelwandler 3,3 V → 5 V am Breadboard — SN74AHCT125N (Draufsicht)",
     size=16, anchor="middle", weight="bold", fill="#111")
text(560, 62, "Schritt-für-Schritt-Anleitung: docs/AUFBAU-PEGELWANDLER.md · "
     "nicht maßstäblich · Schaltung wie in PLAN.md, Abschnitt 5",
     size=10, anchor="middle", fill="#666")

x0, y0, x1, y1 = BOARD
add(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="8" fill="{BG_BOARD}" '
    f'stroke="#999" stroke-width="1.5"/>')

# Schienen, oben und unten
for y, col, sign in [(RED_T, RED, "+"), (BLUE_T, BLUE, "−"),
                     (BLUE_B, BLUE, "−"), (RED_B, RED, "+")]:
    add(f'<line x1="210" y1="{y}" x2="890" y2="{y}" stroke="{col}" stroke-width="2.5"/>')
    for gx in range(262, 870, 66):
        text(gx, y + 4, sign, size=10, fill=col, anchor="middle", weight="bold")
text(196, RED_T + 4, "+5 V", size=10, fill=RED, anchor="end", weight="bold")
text(196, BLUE_T + 4, "GND", size=10, fill=BLUE, anchor="end", weight="bold")
text(196, BLUE_B + 4, "GND", size=10, fill=BLUE, anchor="end", weight="bold")
text(196, RED_B + 4, "+5 V", size=10, fill=RED, anchor="end", weight="bold")

# Mittelluecke
g0, g1 = GROOVE
add(f'<rect x="{x0}" y="{g0}" width="{x1-x0}" height="{g1-g0}" fill="#e6dcbf"/>')
for gy in (g0, g1):
    add(f'<line x1="{x0}" y1="{gy}" x2="{x1}" y2="{gy}" stroke="#b8a888" '
        f'stroke-width="0.8" stroke-dasharray="4 3"/>')
text(712, 337, "Mittellücke (Rinne):", size=8.5, fill="#6b5d33")
text(712, 348, "oben ≠ unten!", size=8.5, fill="#6b5d33")

# Loecher und Spaltennummern
for c in range(15, 32):
    x = colx(c)
    for y in TOP + BOT:
        add(f'<circle cx="{x}" cy="{y}" r="3" fill="{DOT}"/>')
    text(x, 142, str(c), size=10, fill="#888", anchor="middle")
text(208, 126, "Spalten 1–14 liegen links außerhalb des Ausschnitts",
     size=8.5, fill="#888")

# ---------------------------------------------------------------- Leitungen

# +5 V (rot)
wire([(146, 290), (218, 290), (218, RED_T)], RED)                    # Agon Pin 4
for c in (20, 21, 24):                                               # Pin 14, 13, 10
    wire([(colx(c), 228), (colx(c), RED_T)], RED)
wire([(colx(23), 452), (colx(23), RED_B)], RED)                      # Pin 4
wire([(870, RED_T), (910, RED_T), (910, RED_B), (870, RED_B)], RED)  # Bruecke rot

# GND (schwarz)
wire([(146, 330), (230, 330), (230, BLUE_T)], BLK)                   # Agon Pin 3
for c in (22, 25):                                                   # Pin 12, 9
    wire([(colx(c), 228), (colx(c), BLUE_T)], BLK)
for c in (20, 24, 26):                                               # Pin 1, 5, 7
    wire([(colx(c), 452), (colx(c), BLUE_B)], BLK)
wire([(880, BLUE_T), (895, BLUE_T), (895, BLUE_B), (880, BLUE_B)], BLK)  # Bruecke blau
wire([(250, 690), (250, BLUE_B)], BLK)                               # Netzteil Minus

# Daten vom Agon (orange): durch die Mittelluecke, dann in Spalte 21 unten
wire([(146, 370), (190, 370), (190, 340), (410, 340), (410, 408), (colx(21), 408)], ORG)

# Daten zum Modul (gelb), mit der einzigen Kreuzung: 12 V senkrecht bei x = 940
wire([(colx(17), 452), (colx(17), 625), (950, 625)], YEL)
hop(940, 625, YEL, BG)

# Netzteil -> Modul
wire([(426, 710), (925, 710), (925, 670), (950, 670)], BLK)          # GND
wire([(426, 745), (940, 745), (940, 580), (950, 580)], P12)          # +12 V

# ---------------------------------------------------------------- IC

for c in range(20, 27):
    x = colx(c)
    add(f'<line x1="{x}" y1="322" x2="{x}" y2="317" stroke="#777" stroke-width="3"/>')
    add(f'<line x1="{x}" y1="358" x2="{x}" y2="363" stroke="#777" stroke-width="3"/>')
    plug(x, 316, "#777", r=3.5)
    plug(x, 364, "#777", r=3.5)
add('<rect x="428" y="322" width="264" height="36" rx="3" fill="#2b2b2b" '
    'stroke="#111" stroke-width="1"/>')
add(f'<circle cx="428" cy="340" r="7" fill="{BG_BOARD}" stroke="#111" stroke-width="1"/>')
for i, c in enumerate(range(20, 27)):
    x = colx(c)
    text(x, 338, str(14 - i), size=9.5, fill="#fff", anchor="middle", weight="bold")
    text(x, 354, str(1 + i), size=9.5, fill="#fff", anchor="middle", weight="bold")
add('<circle cx="440" cy="364" r="8" fill="none" stroke="#d32f2f" stroke-width="1.75"/>')
text(452, 384, "Pin 1", size=9, fill=RED, weight="bold", halo=True)

# ---------------------------------------------------------------- Bauteile

# 100 nF direkt zwischen oberer roter und blauer Schiene (neben Spalte 19)
add(f'<line x1="400" y1="{RED_T}" x2="400" y2="{BLUE_T}" stroke="{LEG}" stroke-width="2"/>')
add('<circle cx="400" cy="187" r="9" fill="#d9a441" stroke="#8a6d1f" stroke-width="1.25"/>')
text(400, 189.5, "104", size=6.5, fill="#5d4a12", anchor="middle", weight="bold")
text(386, 191, "100 nF", size=8.5, fill="#555", anchor="end", halo=True)

# 8,2 kOhm: Spalte 21 unten -> untere blaue Schiene
add(f'<line x1="{colx(21)}" y1="452" x2="{colx(21)}" y2="{BLUE_B}" stroke="{LEG}" stroke-width="2"/>')
resistor_v(colx(21), 476, [GREY, REDB, REDB], "8,2 kΩ")

# 390 Ohm: Spalte 22 unten -> Spalte 17 unten (Zeile 430)
add(f'<line x1="{colx(17)}" y1="430" x2="{colx(22)}" y2="430" stroke="{LEG}" stroke-width="2"/>')
resistor_h(380, 430, [ORANGE, WHITE, BROWN], "390 Ω")

# ---------------------------------------------------------------- Punkte (verbunden)

for x, y in [(218, RED_T), (400, RED_T), (colx(20), RED_T), (colx(21), RED_T),
             (colx(24), RED_T), (870, RED_T), (colx(23), RED_B), (870, RED_B),
             (colx(20), 228), (colx(21), 228), (colx(24), 228), (colx(23), 452)]:
    plug(x, y, RED)
for x, y in [(230, BLUE_T), (400, BLUE_T), (colx(22), BLUE_T), (colx(25), BLUE_T),
             (880, BLUE_T), (250, BLUE_B), (colx(20), BLUE_B), (colx(21), BLUE_B),
             (colx(24), BLUE_B), (colx(26), BLUE_B), (880, BLUE_B),
             (colx(22), 228), (colx(25), 228), (colx(20), 452), (colx(24), 452),
             (colx(26), 452)]:
    plug(x, y, BLK)
plug(colx(21), 452, LEG)            # 8,2 kOhm
plug(colx(17), 430, LEG)            # 390 Ohm
plug(colx(22), 430, LEG)
plug(colx(21), 408, ORG)            # Daten vom Agon
plug(colx(17), 452, YEL)            # Daten zum Modul

# ---------------------------------------------------------------- Schrittnummern

badge(406, 310, "1")                # IC
badge(902, 351, "2")                # Bruecken
badge(458, 214, "3")                # IC-Strom (Pin 14 / Pin 7)
badge(700, 478, "3")
badge(382, 160, "4")                # 100 nF
badge(620, 214, "5")                # unbenutzte Kanaele oben
badge(580, 478, "5")                # unbenutzte Kanaele unten
badge(460, 478, "6")                # Pin 1
badge(536, 494, "7")                # 8,2 kOhm
badge(380, 412, "8")                # 390 Ohm
badge(172, 266, "10")               # Agon

# ---------------------------------------------------------------- Agon

add('<rect x="20" y="250" width="120" height="180" rx="6" fill="#263238" stroke="#111"/>')
text(80, 272, "Agon Light 2", size=10, fill="#fff", anchor="middle", weight="bold")
for ty, lbl in [(284, "Pin 4 +5 V"), (324, "Pin 3 GND"), (364, "Pin 21 PC4")]:
    add(f'<rect x="134" y="{ty}" width="12" height="12" rx="1.5" fill="#cfd8dc" stroke="#111"/>')
    text(130, ty + 10, lbl, size=8.5, fill="#fff", anchor="end")
text(80, 452, "Nur diese 3 Kabel", size=9, fill="#555", anchor="middle")
text(80, 464, "zum Breadboard!", size=9, fill="#555", anchor="middle")
text(80, 482, "Pinlage vorher mit dem", size=8.5, fill=RED, anchor="middle", weight="bold")
text(80, 494, "Multimeter prüfen (⑨)", size=8.5, fill=RED, anchor="middle", weight="bold")
text(150, 284, "+5 V (Pin 4)", size=9, fill=RED, weight="bold", halo=True)
text(150, 324, "GND (Pin 3)", size=9, fill=BLK, weight="bold", halo=True)
text(150, 386, "PC4 Daten (Pin 21)", size=9, fill=ORG, weight="bold", halo=True)

# ---------------------------------------------------------------- Modul

add('<rect x="950" y="560" width="250" height="155" rx="6" fill="#1e1e1e" stroke="#000"/>')
text(1120, 580, "Testmodul", size=10, fill="#fff", anchor="middle", weight="bold")
badge(1184, 576, "11")
for ty, lbl in [(575, "+12 V"), (620, "DIN (Daten)"), (665, "GND")]:
    add(f'<rect x="945" y="{ty}" width="10" height="10" rx="1.5" fill="#cfd8dc" stroke="#111"/>')
    text(962, ty + 9, lbl, size=8.5, fill="#fff")
for i in range(4):
    px = 1065 + i * 32
    add(f'<rect x="{px}" y="600" width="28" height="28" rx="2" fill="#333" stroke="#555"/>')
    for dx in (-6, 6):
        add(f'<circle cx="{px+14+dx}" cy="614" r="4" fill="{"#ffffff" if i == 0 else "#555"}"/>')
text(1127, 646, "erste LED = Pixel 0 (links)", size=8, fill="#bbb", anchor="middle")
text(1075, 690, "Stecker JST XH: 12 V · Daten · GND", size=8, fill="#bbb", anchor="middle")
text(1075, 704, "4 Pixel · 2 LEDs je Pixel = 8 LEDs", size=8, fill="#bbb", anchor="middle")
text(950, 738, "⑫ Arduino (Pin 13) von der Datenleitung trennen!",
     size=10, fill=RED, weight="bold")

text(600, 618, "Daten 5 V → Modul DIN (gelb)", size=9, fill=YEL, weight="bold", halo=True)
text(600, 703, "GND (−) zum Modul", size=9, fill=BLK, weight="bold", halo=True)
text(600, 738, "12 V (+) nur zum Modul", size=9, fill=P12, weight="bold", halo=True)

# ---------------------------------------------------------------- Netzteil

add('<rect x="220" y="690" width="200" height="80" rx="4" fill="#37474f" stroke="#111"/>')
text(320, 736, "12-V-Netzteil", size=10, fill="#fff", anchor="middle", weight="bold")
add('<rect x="245" y="684" width="10" height="10" rx="1.5" fill="#cfd8dc" stroke="#111"/>')
text(262, 706, "− zur Schiene", size=8.5, fill="#fff")
add('<rect x="416" y="705" width="10" height="10" rx="1.5" fill="#cfd8dc" stroke="#111"/>')
text(410, 714, "− GND", size=8.5, fill="#fff", anchor="end")
add('<rect x="416" y="740" width="10" height="10" rx="1.5" fill="#cfd8dc" stroke="#111"/>')
text(410, 749, "+12 V", size=8.5, fill="#fff", anchor="end")

# ---------------------------------------------------------------- Legende

add('<rect x="940" y="150" width="275" height="318" rx="6" fill="#fafafa" stroke="#bbb"/>')
text(950, 168, "Legende", size=12, weight="bold", fill="#111")
swatches = [(RED, "+5 V: Leitungen und rote Schienen"),
            (BLK, "GND: Leitungen; blaue Schienen"),
            (ORG, "Daten Agon → Wandler (3,3 V)"),
            (YEL, "Daten Wandler → LEDs (5 V)"),
            (P12, "12 V: nur Netzteil → Modul"),
            ("#e8d5a3", "Bauteile, Beinchen grau")]
for i, (c, lbl) in enumerate(swatches):
    sy = 178 + i * 14
    add(f'<rect x="950" y="{sy}" width="14" height="6" fill="{c}" stroke="#888" stroke-width="0.5"/>')
    text(970, sy + 6, lbl, size=9, fill="#333")
notes = ["Verbunden ist nur, wo ein Punkt sitzt.",
         "Leitungen über Schienen oder Löcher ohne",
         "Punkt sind dort NICHT verbunden.",
         "Bogen = Kreuzung ohne Verbindung.",
         "Rinne: obere und untere Lochhälfte",
         "einer Spalte sind NICHT verbunden.",
         "Roter Kreis = Pin 1 des IC (neben der Kerbe).",
         "Nummernkreise = Schritt in der Anleitung."]
ny = 270
for n in notes:
    text(950, ny, n, size=8.5, fill="#555")
    ny += 12
text(950, 372, "IC-Pins (Spalten 20–26):", size=9, weight="bold", fill="#111")
pin_table = ["14 VCC → +5 V oben · 7 GND → GND unten",
             "1 OE̅1 → GND unten (Kanal 1 immer an)",
             "2 1A ← Agon Pin 21 · 8,2 kΩ → GND unten",
             "3 1Y → 390 Ω → Spalte 17 → Modul",
             "13, 10 → +5 V oben · 4 → +5 V unten",
             "12, 9 → GND oben · 5 → GND unten",
             "6, 8, 11 bleiben frei"]
py = 386
for row in pin_table:
    text(950, py, row, size=8.5, fill="#333")
    py += 11.5

add(f'<rect x="940" y="476" width="275" height="64" rx="4" fill="#fdecea" stroke="{RED}" '
    f'stroke-width="1.5"/>')
text(950, 492, "ACHTUNG — 12 V und 5 V trennen!", size=10, fill=RED, weight="bold")
text(950, 507, "Vom Netzteil kommt NUR Minus ans Breadboard.", size=8.5, fill="#7a2a24")
text(950, 519, "Die 12-V-Leitung (lila) geht direkt ans Modul —", size=8.5, fill="#7a2a24")
text(950, 531, "niemals an eine rote Schiene (5 V)!", size=8.5, fill="#7a2a24")

text(20, 800, "Gemeinsame Masse ist Pflicht: Agon GND (Pin 3), Netzteil-Minus und Modul-GND "
     "treffen sich auf den blauen Schienen (oben und unten über ② verbunden).",
     size=9, fill="#555")
text(20, 816, "Welche Schiene außen und welche innen liegt, ist je nach Breadboard verschieden "
     "— maßgeblich ist die Markierung (+ rot, − blau).", size=9, fill="#555")

add("</svg>")

# ---------------------------------------------------------------- Schreiben

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "bilder", "breadboard-pegelwandler.svg")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(S) + "\n")
print("OK " + out)
