# -*- coding: utf-8 -*-
"""Erzeugt den Lochraster-Bauplan fuer den Pegelwandler (docs/bilder/).

Draufsicht auf eine Universal-Lochrasterplatine 5x7 cm (20x28 Loecher,
Raster 2,54 mm) mit SN74AHCT125N, 390 Ohm, 8,2 kOhm, 100 nF und drei
Stiftleisten (J1 Agon, J2 Modul, J3 Netzteil). Elektrisch identisch mit
dem Breadboard-Aufbau aus docs/AUFBAU-PEGELWANDLER.md.

Zeichenregeln:
- Die Litzen laufen auf der Loetseite und duerfen andere Loecher kreuzen;
  verbunden ist nur, was am Pad veroetet ist (dunkle Ringe = Mehrfachpads).
- Die 12-V-Leitung (lila) fuehrt ausschliesslich am Platinenrand.

Aufruf:  python scripts/gen_perfboard_svg.py  [ausgabedatei]
"""

import os
import sys

RED = "#d32f2f"       # +5 V
BLK = "#212121"       # GND
ORG = "#ef6c00"       # Daten 3,3 V vom Agon
YEL = "#c89000"       # Daten 5 V zum Modul
P12 = "#8e24aa"       # 12 V
LEG = "#8d8d8d"       # Bauteil-Beinchen
DOT = "#b8a888"       # unbenutzte Loecher
BG = "#e6dfc4"        # Platinengrund

W, H = 1400, 850
X0, Y0 = 90, 100      # Loch (1,1)
DX, DY = 26, 24       # Raster (nicht massstabsgetreu gezeichnet)

S = []


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add(s):
    S.append(s)


def X(c):
    return X0 + (c - 1) * DX


def Y(r):
    return Y0 + (r - 1) * DY


def text(x, y, t, size=9, fill="#333", anchor="start", weight="normal",
         halo=False):
    extra = ' stroke="#ffffff" stroke-width="3" paint-order="stroke"' if halo \
        else ""
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}"{extra}>{esc(t)}</text>')


def wire(points, color, w=3.5):
    pts = " ".join(f"{X(c)},{Y(r)}" for c, r in points)
    add(f'<polyline points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def junction(c, r):
    add(f'<circle cx="{X(c)}" cy="{Y(r)}" r="6" fill="none" stroke="#333" '
        f'stroke-width="1.6"/>')


def resistor_h(c1, c2, r, bands, label):
    x1, x2 = X(c1), X(c2)
    xc = (x1 + x2) / 2
    y = Y(r)
    add(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{LEG}" '
        f'stroke-width="2.5"/>')
    add(f'<rect x="{xc-22}" y="{y-7}" width="44" height="14" rx="6" '
        f'fill="#e8d5a3" stroke="#8a7a4a"/>')
    for i, b in enumerate(bands):
        add(f'<rect x="{xc-14+i*8}" y="{y-7}" width="4" height="14" '
            f'fill="{b}"/>')
    text(xc, y + 22, label, size=8.5, fill="#555", anchor="middle", halo=True)


# ---------------------------------------------------------------- Grundgeruest

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

text(700, 40, "Pegelwandler auf Lochraster 5\u00d77 cm \u2014 SN74AHCT125N "
     "(Draufsicht)", size=16, anchor="middle", weight="bold", fill="#111")
text(700, 64, "Gleiche Schaltung wie das Breadboard \u00b7 Verdrahtung auf der "
     "L\u00f6tseite (Unterseite) \u00b7 Raster 2,54 mm \u00b7 20\u00d728 L\u00f6cher",
     size=10, anchor="middle", fill="#666")

# Platte
add(f'<rect x="62" y="82" width="552" height="686" rx="8" fill="{BG}" '
    f'stroke="#8a8264" stroke-width="1.5"/>')
for c in range(1, 21):
    for r in range(1, 29):
        add(f'<circle cx="{X(c)}" cy="{Y(r)}" r="3.2" fill="{DOT}"/>')

text(X(10), 74, "20 L\u00f6cher = 5 cm", size=9, fill="#888", anchor="middle")
add(f'<text x="{X(20)+26}" y="{Y(14)}" font-size="9" fill="#888" '
    f'transform="rotate(90 {X(20)+26} {Y(14)})" text-anchor="middle">'
    f'28 L\u00f6cher = 7 cm</text>')

# ---------------------------------------------------------------- 12-V-Randpfad

wire([(3, 25), (3, 28), (19, 28), (19, 20), (18, 20)], P12, w=4)

# ---------------------------------------------------------------- GND-Netz

wire([(2, 5), (2, 14), (6, 14)], BLK)            # J1 GND -> Pin 1 (ueber C1)
wire([(8, 11), (11, 11)], BLK)                   # Pin 12 -> Pin 9
wire([(8, 11), (8, 16), (4, 16), (4, 14)], BLK)  # Pin 12 -> C1 Bein 2
wire([(10, 14), (12, 14)], BLK)                  # Pin 5 -> Pin 7
wire([(7, 14), (7, 17)], BLK)                    # Pin 2 -> R2
wire([(9, 17), (9, 14), (10, 14)], BLK)          # R2 -> Pin 5 (GND)
wire([(12, 14), (17, 14), (17, 26), (18, 26)], BLK)  # Pin 7 -> J2 GND
wire([(12, 14), (12, 27), (3, 27)], BLK)         # Pin 7 -> J3 GND

# ---------------------------------------------------------------- +5-V-Netz

wire([(2, 3), (2, 11), (6, 11)], RED)            # J1 +5V -> Pin 14
wire([(6, 11), (4, 11)], RED)                    # Pin 14 -> C1 Bein 1
wire([(7, 11), (10, 11)], RED)                   # Pin 13 -> Pin 10
wire([(10, 11), (10, 8), (6, 8), (6, 11)], RED)  # Pin 10 -> Pin 14
wire([(9, 14), (6, 17), (4, 17), (4, 11)], RED)  # Pin 4 -> C1 Bein 1

# ---------------------------------------------------------------- Daten

wire([(2, 7), (7, 7), (7, 14)], ORG)             # J1 PC4 -> Pin 2
wire([(8, 14), (10, 17)], YEL)                   # Pin 3 -> R1
wire([(13, 17), (15, 17), (15, 23), (18, 23)], YEL)  # R1 -> J2 DIN

# ---------------------------------------------------------------- Bauteile

resistor_h(10, 13, 17, ["#ef6c00", "#ffffff", "#6b3f1d"], "390 \u03a9")
resistor_h(7, 9, 17, ["#9e9e9e", "#c62828", "#c62828"], "8,2 k\u03a9")

# C1: Spalte 4 zwischen Reihe 11 (+5 V) und Reihe 14 (GND)
add(f'<line x1="{X(4)}" y1="{Y(11)}" x2="{X(4)}" y2="{Y(12)}" stroke="{LEG}" '
    f'stroke-width="2.5"/>')
add(f'<line x1="{X(4)}" y1="{Y(14)}" x2="{X(4)}" y2="{Y(13)}" stroke="{LEG}" '
    f'stroke-width="2.5"/>')
add(f'<circle cx="{X(4)}" cy="{(Y(12)+Y(13))/2}" r="11" fill="#d9a441" '
    f'stroke="#8a6d1f" stroke-width="1.25"/>')
text(X(4) - 16, (Y(12) + Y(13)) / 2 + 4, "100 nF", size=8.5, fill="#555",
     anchor="end", halo=True)

# ---------------------------------------------------------------- IC

add('<rect x="206" y="348" width="184" height="56" rx="4" fill="#2b2b2b" '
    'stroke="#111"/>')
add('<circle cx="206" cy="376" r="7" fill="#e6dfc4" stroke="#111"/>')
for i, c in enumerate(range(6, 13)):
    x = X(c)
    add(f'<line x1="{x}" y1="348" x2="{x}" y2="{Y(11)}" stroke="{LEG}" '
        f'stroke-width="3"/>')
    add(f'<line x1="{x}" y1="404" x2="{x}" y2="{Y(14)}" stroke="{LEG}" '
        f'stroke-width="3"/>')
    add(f'<circle cx="{x}" cy="{Y(11)}" r="3.8" fill="{LEG}"/>')
    add(f'<circle cx="{x}" cy="{Y(14)}" r="3.8" fill="{LEG}"/>')
    text(x, 368, str(14 - i), size=9.5, fill="#fff", anchor="middle",
         weight="bold")
    text(x, 396, str(i + 1), size=9.5, fill="#fff", anchor="middle",
         weight="bold")
text(298, 380, "SN74AHCT125N", size=9, fill="#9e9e9e", anchor="middle")
add('<circle cx="220" cy="412" r="8" fill="none" stroke="#d32f2f" '
    'stroke-width="1.75"/>')
text(232, 428, "Pin 1", size=9, fill="#d32f2f", weight="bold", halo=True)

# ---------------------------------------------------------------- Stiftleisten

def header(c1, r1, r2, pin_rows, title, labels, label_side, title_dy):
    x1, x2 = X(c1) - 14, X(c1) + 14
    y1, y2 = Y(r1) - 10, Y(r2) + 10
    add(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="3" '
        f'fill="#37474f" stroke="#111"/>')
    for pr in pin_rows:
        add(f'<rect x="{X(c1)-5}" y="{Y(pr)-5}" width="10" height="10" rx="1.5" '
            f'fill="#cfd8dc" stroke="#111"/>')
    ty = y1 - 6 if title_dy < 0 else y2 + 14
    text(X(c1), ty, title, size=9.5, fill="#111", anchor="middle",
         weight="bold")
    for pr, lbl in pin_rows and zip(pin_rows, labels):
        if label_side == "right":
            text(X(c1) + 20, Y(pr) + 4, lbl, size=8.5, fill="#333",
                 weight="bold", halo=True)
        else:
            text(X(c1) - 20, Y(pr) + 4, lbl, size=8.5, fill="#333",
                 anchor="end", weight="bold", halo=True)


header(2, 3, 7, [3, 5, 7], "J1 \u2192 Agon",
       ["+5 V (Pin 4)", "GND (Pin 3)", "PC4 (Pin 21)"], "right", -1)
header(18, 20, 26, [20, 23, 26], "J2 \u2192 Modul",
       ["12 V", "DIN (Daten)", "GND"], "right", -1)
header(3, 25, 27, [25, 27], "J3 \u2190 Netzteil",
       ["12 V", "GND"], "left", +1)

# ---------------------------------------------------------------- Mehrfach-Pads

for c, r in [(4, 11), (4, 14), (6, 11), (6, 14), (7, 14), (10, 14), (12, 14)]:
    junction(c, r)

# ---------------------------------------------------------------- Warnung 12 V

text(62, 792, "\u26a0 Lila = 12 V: f\u00fchrt NUR am Platinenrand "
     "(unten/rechts) und ist dort von allen 5-V-/GND-Leitungen ferngehalten. "
     "Nie mit rot oder schwarz verl\u00f6ten!",
     size=9.5, fill="#8e24aa", weight="bold")

# ---------------------------------------------------------------- Legende

add('<rect x="660" y="90" width="710" height="640" rx="6" fill="#fafafa" '
    'stroke="#bbb"/>')
text(672, 112, "Legende & Anschlussbelegung", size=13, weight="bold",
     fill="#111")

sw = [(RED, "+5 V-Leitungen (vom Agon Pin 4)"),
      (BLK, "GND/Masse-Leitungen"),
      (ORG, "Daten Agon \u2192 Wandler (3,3 V)"),
      (YEL, "Daten Wandler \u2192 Modul (5 V)"),
      (P12, "12 V \u2014 nur Randpfad"),
      (LEG, "Bauteile-Beinchen / Br\u00fccken")]
yy = 130
for c, lbl in sw:
    add(f'<line x1="672" y1="{yy}" x2="700" y2="{yy}" stroke="{c}" '
        f'stroke-width="4" stroke-linecap="round"/>')
    text(710, yy + 4, lbl, size=9, fill="#333")
    yy += 15

notes = [
    "Verbindung hat nur, was am Pad verl\u00f6tet ist (dunkler Ring =",
    "Mehrfach-Pad). Litzen d\u00fcrfen L\u00f6cher kreuzen \u2014 sie liegen",
    "isoliert auf der L\u00f6tseite.",
    "",
    "Stiftleisten mit den Pins nach oben einl\u00f6ten:",
    "J1 (3-polig) \u2192 Agon: +5 V / GND / PC4 per Buchsenkabel,",
    "J2 (3-polig) \u2192 Modul in JST-Reihenfolge 12 V\u00b7Daten\u00b7GND,",
    "J3 (2-polig) \u2190 Netzteil 12 V (VARTA o. \u00e4., Testmodul).",
]
yy += 8
for n in notes:
    if n:
        text(672, yy, n, size=8.5, fill="#555")
    yy += 12

text(672, yy + 6, "Anschl\u00fcsse:", size=9, weight="bold", fill="#111")
yy += 20
anschl = [("J1.1", "+5 V (Agon Pin 4)"), ("J1.2", "GND (Agon Pin 3)"),
          ("J1.3", "PC4 (Agon Pin 21)"), ("J2.1", "12 V \u2192 Modul"),
          ("J2.2", "Daten \u2192 Modul (DIN)"), ("J2.3", "GND \u2192 Modul"),
          ("J3.1", "12 V vom Netzteil"), ("J3.2", "GND vom Netzteil")]
for pin, lbl in anschl:
    text(672, yy, pin, size=8.5, weight="bold", fill="#333")
    text(720, yy, lbl, size=8.5, fill="#333")
    yy += 12

text(672, yy + 8, "Komponenten: IC SN74AHCT125N (Kerbe links, Pin 1 unten "
     "links) \u00b7 R1 390 \u03a9 (Daten) \u00b7 R2 8,2 k\u03a9 (Pull-down) \u00b7 "
     "C1 100 nF (direkt am IC). Optional: 14-polige IC-Fassung.", size=8.5,
     fill="#555")
yy += 24
text(672, yy + 6, "Pr\u00fcfen vor dem ersten Strom (Durchgangspr\u00fcfer):",
     size=9, weight="bold", fill="#8e24aa")
checks = [
    "J2.1 \u2014 J3.1: 0 \u03a9 (12 V durchverbunden)",
    "J3.1 gegen J1.1 / J2.3 / J3.2: unendlich (12 V getrennt!)",
    "J1.1 \u2014 IC Pin 14: 0 \u03a9 \u00b7 J1.2 \u2014 IC Pin 1: 0 \u03a9",
    "J1.3 \u2014 IC Pin 2: 0 \u03a9 \u00b7 IC Pin 14 \u2014 IC Pin 1: > 500 \u03a9",
]
yy += 22
for n in checks:
    text(672, yy, n, size=8.5, fill="#7a2a24")
    yy += 12

add("</svg>")

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "bilder", "lochraster-pegelwandler.svg")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(S) + "\n")
print("OK " + out)
