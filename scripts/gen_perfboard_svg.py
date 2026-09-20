# -*- coding: utf-8 -*-
"""Erzeugt den Lochraster-Bauplan fuer den Pegelwandler (docs/bilder/).

Draufsicht auf eine Universal-Lochrasterplatine 5x7 cm mit 18x24 Loechern
(Raster 2,54 mm) und SN74AHCT125N, 390 Ohm, 8,2 kOhm, 100 nF sowie drei
Stiftleisten (J1 Agon, J2 Modul, J3 Netzteil). Elektrisch identisch mit dem
Breadboard-Aufbau aus docs/AUFBAU-PEGELWANDLER.md.

Beschriftung wie auf der Platine des Nutzers:
  Reihen  A (oben) ... X (unten)
  Spalten 18 (links) ... 01 (rechts)
Ein Pad heisst deshalb z. B. "J14" = Reihe J, Spalte 14.

Zeichenregeln:
- Die Litzen laufen auf der Loetseite und duerfen fremde Loecher kreuzen;
  verbunden ist nur, was am Pad verloetet ist (dunkle Ringe = Mehrfachpads).
  Kreuzungen werden als Bruecke (Halbbogen) gezeichnet.
- Keine Litze laeuft ueber ein Pad eines fremden Netzes - das prueft
  check_netz() beim Erzeugen und meldet jeden Verstoss.
- Die 12-V-Leitung (lila) fuehrt ausschliesslich in der rechten unteren Ecke.
- Kabel nach aussen enden als beschriftete Linien am Bildrand.

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

FARBE = {"+5V": RED, "GND": BLK, "DIN": ORG, "DOUT": YEL, "12V": P12}

W, H = 1680, 900
NCOL, NROW = 18, 24   # Spalten, Reihen
ROWS = "ABCDEFGHIJKLMNOPQRSTUVWX"
X0, Y0 = 230, 150     # Pad A18 (links oben)
DX, DY = 26, 24       # Raster (nicht massstabsgetreu gezeichnet)
PL, PT = X0 - 28, Y0 - 28                    # Platinenrand links/oben
PR, PB = X0 + 17 * DX + 28, Y0 + 23 * DY + 28

S = []


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add(s):
    S.append(s)


def pad(name):
    """'J14' -> (x, y) in Bildkoordinaten."""
    r = ROWS.index(name[0])
    c = int(name[1:])
    return X0 + (NCOL - c) * DX, Y0 + r * DY


def text(x, y, t, size=9, fill="#333", anchor="start", weight="normal",
         halo=False, extra=""):
    h = ' stroke="#ffffff" stroke-width="3" paint-order="stroke"' if halo else ""
    add(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}"{h}{extra}>'
        f'{esc(t)}</text>')


# ------------------------------------------------------------------- Netzliste
# (Netz, Pfad ueber Pads, Zweck).  Jeder Knick liegt auf einem Pad.

WIRES = [
    ("+5V",  "C18 C06", "J1.1 +5 V -> 5-V-Schiene"),
    ("+5V",  "C06 P06", "5-V-Schiene (Spalte 06)"),
    ("+5V",  "H14 H06", "5-V-Brücke über dem IC (Reihe H)"),
    ("+5V",  "J14 H14", "IC Pin 14 VCC"),
    ("+5V",  "J13 H13", "IC Pin 13 (OE4) -> VCC"),
    ("+5V",  "J10 H10", "IC Pin 10 (OE3) -> VCC"),
    ("+5V",  "M11 P11 P06", "IC Pin 4 (OE2) -> VCC"),
    ("GND",  "E18 E16 N16", "J1.3 GND -> GND-Bus"),
    ("GND",  "N16 N03 P03 P01", "GND-Bus (Reihe N) -> J2.1"),
    ("GND",  "M14 N14", "IC Pin 1 (OE1) -> GND"),
    ("GND",  "M10 N10", "IC Pin 5 (2A) -> GND"),
    ("GND",  "M08 N08", "IC Pin 7 GND"),
    ("GND",  "J12 I12 I07 N07", "IC Pin 12 (4A) -> GND"),
    ("GND",  "J09 I09", "IC Pin 9 (3A) -> GND"),
    ("GND",  "Q15 N15", "R2 (Pull-down) -> GND"),
    ("GND",  "X03 X05 N05", "J3.2 GND -> GND-Bus"),
    ("DIN",  "D18 D17 R17 R13 M13", "J1.2 PC4 -> IC Pin 2"),
    ("DOUT", "M12 Q12", "IC Pin 3 -> R1"),
    ("DOUT", "Q09 Q01", "R1 -> J2.2 DIN"),
    ("12V",  "X02 X01 R01", "J3.1 -> J2.3 (nur Randpfad!)"),
]

# Bauteile: (Netz-egal) Beinchen-Pads, Typ
BAUTEILE = [
    ("R1", "Q12", "Q09", "390 Ω", ["#ef6c00", "#ffffff", "#6b3f1d"]),
    ("R2", "Q15", "Q13", "8,2 kΩ", ["#9e9e9e", "#c62828", "#c62828"]),
]

# Pads mit Netz, die kein Litzenende sind (Bauteilbeine, IC-Pins)
EXTRA_PADS = [
    ("Q12", "DOUT", "R1 Bein 1"), ("Q09", "DOUT", "R1 Bein 2"),
    ("Q15", "GND", "R2 Bein 1"), ("Q13", "DIN", "R2 Bein 2"),
    ("H08", "+5V", "C1 Bein 1"), ("I08", "GND", "C1 Bein 2"),
]

# IC-Pins: Nummer -> Pad (Kerbe links, Pin 1 unten links)
IC_OBEN = {14: "J14", 13: "J13", 12: "J12", 11: "J11", 10: "J10",
           9: "J09", 8: "J08"}
IC_UNTEN = {1: "M14", 2: "M13", 3: "M12", 4: "M11", 5: "M10",
            6: "M09", 7: "M08"}
IC_NETZ = {14: "+5V", 13: "+5V", 10: "+5V", 4: "+5V",
           1: "GND", 12: "GND", 9: "GND", 5: "GND", 7: "GND",
           2: "DIN", 3: "DOUT"}

# --------------------------------------------------------------- Netzpruefung

def wire_pads(w):
    return w[1].split()


def segments():
    """[(x1, y1, x2, y2, netz, index)] aller Litzenstuecke."""
    out = []
    for i, w in enumerate(WIRES):
        ps = wire_pads(w)
        for a, b in zip(ps, ps[1:]):
            (x1, y1), (x2, y2) = pad(a), pad(b)
            out.append((x1, y1, x2, y2, w[0], i))
    return out


def check_netz():
    """Meldet Pads mit zwei Netzen und Litzen ueber fremden Pads."""
    fehler = []
    netz_von_pad = {}
    zaehler = {}
    for w in WIRES:
        for p in wire_pads(w):
            netz_von_pad.setdefault(p, w[0])
            zaehler[p] = zaehler.get(p, 0) + 1
            if netz_von_pad[p] != w[0]:
                fehler.append(f"Pad {p}: {netz_von_pad[p]} und {w[0]}")
    for p, n, _ in EXTRA_PADS:
        if netz_von_pad.setdefault(p, n) != n:
            fehler.append(f"Pad {p}: {netz_von_pad[p]} und {n}")
        zaehler[p] = zaehler.get(p, 0) + 1
    for nr, p in list(IC_OBEN.items()) + list(IC_UNTEN.items()):
        n = IC_NETZ.get(nr)
        if n:
            if netz_von_pad.setdefault(p, n) != n:
                fehler.append(f"IC-Pin {nr} ({p}): {netz_von_pad[p]} und {n}")
        elif p in netz_von_pad:
            fehler.append(f"IC-Pin {nr} ({p}) ist offen, traegt aber eine Litze")
    for x1, y1, x2, y2, netz, i in segments():
        for p, n in netz_von_pad.items():
            px, py = pad(p)
            innen = (min(x1, x2) < px < max(x1, x2) and py == y1 == y2) or \
                    (min(y1, y2) < py < max(y1, y2) and px == x1 == x2)
            if not innen:
                continue
            if n != netz:
                fehler.append(f"Litze {netz} ({WIRES[i][1]}) laeuft ueber "
                              f"Pad {p} ({n})")
            else:
                zaehler[p] = zaehler.get(p, 0) + 1   # T-Stoss auf dem Pad
    return fehler, zaehler


def kreuzungen():
    """{Segment-Index: [x, ...]} - Bruecken auf den waagerechten Stuecken."""
    segs = segments()
    out = {}
    for si, (x1, y1, x2, y2, n1, w1) in enumerate(segs):
        if y1 != y2:
            continue
        for (a1, b1, a2, b2, n2, w2) in segs:
            if a1 != a2 or w1 == w2:
                continue
            if min(x1, x2) < a1 < max(x1, x2) and \
               min(b1, b2) < y1 < max(b1, b2):
                out.setdefault(si, []).append(a1)
    return out


FEHLER, PADZAHL = check_netz()
for f in FEHLER:
    print("FEHLER: " + f, file=sys.stderr)
KREUZ = kreuzungen()

# ------------------------------------------------------------------ Zeichnung

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

text(W / 2, 40, "Pegelwandler auf Lochraster 5×7 cm — SN74AHCT125N "
     "(Draufsicht, Bauteilseite)", size=17, anchor="middle", weight="bold",
     fill="#111")
text(W / 2, 64, "Reihen A–X, Spalten 18 (links) bis 01 (rechts) — wie "
     "auf der Platine aufgedruckt · Raster 2,54 mm · 18×24 Löcher "
     "· Verdrahtung auf der Lötseite", size=10.5, anchor="middle",
     fill="#666")

# Platte und Loecher
add(f'<rect x="{PL}" y="{PT}" width="{PR-PL}" height="{PB-PT}" rx="8" '
    f'fill="{BG}" stroke="#8a8264" stroke-width="1.5"/>')
for r in ROWS:
    for c in range(1, NCOL + 1):
        x, y = pad(f"{r}{c:02d}")
        add(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{DOT}"/>')

# Rasterbeschriftung (Seiten mit Kabelausgang bleiben frei)
OHNE_LINKS = {"C", "D", "E"}
OHNE_RECHTS = {"P", "Q", "R"}
OHNE_UNTEN = {2, 3}
for i, r in enumerate(ROWS):
    y = Y0 + i * DY + 3.5
    if r not in OHNE_LINKS:
        text(PL - 9, y, r, size=9, fill="#7a7259", anchor="middle",
             weight="bold")
    if r not in OHNE_RECHTS:
        text(PR + 9, y, r, size=9, fill="#7a7259", anchor="middle",
             weight="bold")
for c in range(1, NCOL + 1):
    x = X0 + (NCOL - c) * DX
    text(x, PT - 9, f"{c:02d}", size=8.5, fill="#7a7259", anchor="middle",
         weight="bold")
    if c not in OHNE_UNTEN:
        text(x, PB + 15, f"{c:02d}", size=8.5, fill="#7a7259",
             anchor="middle", weight="bold")
text(PL - 9, PT - 9, "•", size=9, fill="#7a7259", anchor="middle")
text((PL + PR) / 2, PT - 26, "18 Löcher = 5 cm", size=9, fill="#888",
     anchor="middle")
add(f'<text x="{PR+26}" y="{(PT+PB)/2}" font-size="9" fill="#888" '
    f'transform="rotate(90 {PR+26} {(PT+PB)/2})" text-anchor="middle">'
    f'24 Löcher = 7 cm</text>')

# ------------------------------------------------------------------- Litzen

HOP = 5.5


def draw_wires():
    si = -1
    for i, w in enumerate(WIRES):
        ps = wire_pads(w)
        x, y = pad(ps[0])
        d = [f"M {x} {y}"]
        for a, b in zip(ps, ps[1:]):
            si += 1
            (x1, y1), (x2, y2) = pad(a), pad(b)
            xs = KREUZ.get(si, [])
            if y1 == y2 and xs:
                schritt = 1 if x2 > x1 else -1
                for xc in sorted(xs, reverse=schritt < 0):
                    d.append(f"L {xc - HOP*schritt} {y1}")
                    sweep = 1 if schritt > 0 else 0
                    d.append(f"A {HOP} {HOP} 0 0 {sweep} "
                             f"{xc + HOP*schritt} {y1}")
            d.append(f"L {x2} {y2}")
        add(f'<path d="{" ".join(str(s) for s in d)}" fill="none" '
            f'stroke="{FARBE[w[0]]}" stroke-width="3.4" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


draw_wires()

# ----------------------------------------------------------------- Bauteile

def widerstand(p1, p2, label, bands, oben=False, dx=0):
    (x1, y), (x2, _) = pad(p1), pad(p2)
    xc = (x1 + x2) / 2
    add(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{LEG}" '
        f'stroke-width="2.5"/>')
    add(f'<rect x="{xc-24}" y="{y-8}" width="48" height="16" rx="7" '
        f'fill="#e8d5a3" stroke="#8a7a4a"/>')
    for i, b in enumerate(bands):
        add(f'<rect x="{xc-15+i*9}" y="{y-8}" width="4.5" height="16" '
            f'fill="{b}"/>')
    text(xc + dx, y - 16 if oben else y + 25, label, size=9, fill="#444",
         anchor="middle", weight="bold", halo=True)


for name, p1, p2, label, bands in BAUTEILE:
    widerstand(p1, p2, f"{name} {label}", bands, oben=(name == "R2"),
               dx=(-18 if name == "R2" else 0))

# C1 senkrecht zwischen H08 (+5 V) und I08 (GND)
(cx, cy1), (_, cy2) = pad("H08"), pad("I08")
add(f'<line x1="{cx}" y1="{cy1}" x2="{cx}" y2="{cy2}" stroke="{LEG}" '
    f'stroke-width="2.5"/>')
add(f'<circle cx="{cx}" cy="{(cy1+cy2)/2}" r="10" fill="#d9a441" '
    f'stroke="#8a6d1f" stroke-width="1.25"/>')
text(cx, cy1 - 15, "C1 100 nF", size=9, fill="#444", anchor="middle",
     weight="bold", halo=True)

# ----------------------------------------------------------------------- IC

icx1, icy1 = pad("J14")[0] - 13, pad("J14")[1] + 7
icx2, icy2 = pad("J08")[0] + 13, pad("M14")[1] - 7
for nr, p in list(IC_OBEN.items()) + list(IC_UNTEN.items()):
    x, y = pad(p)
    yy = icy1 if nr >= 8 else icy2
    add(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{yy}" stroke="{LEG}" '
        f'stroke-width="3"/>')
add(f'<rect x="{icx1}" y="{icy1}" width="{icx2-icx1}" height="{icy2-icy1}" '
    f'rx="4" fill="#2b2b2b" stroke="#111"/>')
add(f'<path d="M {icx1} {(icy1+icy2)/2-8} A 8 8 0 0 0 {icx1} '
    f'{(icy1+icy2)/2+8}" fill="{BG}" stroke="#111" stroke-width="1"/>')
for nr, p in IC_OBEN.items():
    text(pad(p)[0], icy1 + 14, str(nr), size=9.5, fill="#fff", anchor="middle",
         weight="bold")
for nr, p in IC_UNTEN.items():
    text(pad(p)[0], icy2 - 6, str(nr), size=9.5,
         fill=("#ff8a80" if nr == 1 else "#fff"), anchor="middle",
         weight="bold")
text((icx1 + icx2) / 2, (icy1 + icy2) / 2 + 4, "SN74AHCT125N", size=10,
     fill="#9e9e9e", anchor="middle")
x, y = pad("M14")
add(f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{RED}" '
    f'stroke-width="1.8"/>')
text(x, pad("O14")[1] + 4, "Pin 1", size=9, fill=RED, anchor="middle",
     weight="bold", halo=True)

# ------------------------------------------------------- Pads und Mehrfachpads

for p, n in sorted(PADZAHL.items()):
    x, y = pad(p)
    add(f'<circle cx="{x}" cy="{y}" r="4.2" fill="#5d564044"/>')
    if n >= 2:
        add(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="#2f2a1e" '
            f'stroke-width="1.7"/>')

# ------------------------------------------------- Stiftleisten und Aussenkabel

HEADERS = [("J1 → Agon Light 2", ["C18", "D18", "E18"], "v", -26),
           ("J2 → LED-Modul", ["P01", "Q01", "R01"], "v", -24),
           ("J3 ← Netzteil 12 V", ["X03", "X02"], "h", -24)]

for titel, pads, richtung, dy in HEADERS:
    xs = [pad(p)[0] for p in pads]
    ys = [pad(p)[1] for p in pads]
    if richtung == "v":
        x1, x2 = min(xs) - 11, max(xs) + 11
        y1, y2 = min(ys) - 12, max(ys) + 12
    else:
        x1, x2 = min(xs) - 12, max(xs) + 12
        y1, y2 = min(ys) - 11, max(ys) + 11
    add(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="3" '
        f'fill="#37474f" stroke="#111"/>')
    for p in pads:
        x, y = pad(p)
        add(f'<rect x="{x-5.5}" y="{y-5.5}" width="11" height="11" rx="1.5" '
            f'fill="#cfd8dc" stroke="#111"/>')
    text((min(xs) + max(xs)) / 2, min(ys) + dy, titel, size=10, fill="#111",
         anchor="middle", weight="bold", halo=True)

EXTERN = [
    ("C18", "+5V", "links", "J1.1  +5 V — Agon Pin 4", 0),
    ("D18", "DIN", "links", "J1.2  PC4 Daten — Agon Pin 21", 0),
    ("E18", "GND", "links", "J1.3  GND — Agon Pin 3", 0),
    ("P01", "GND", "rechts", "J2.1  GND → LED-Modul", 0),
    ("Q01", "DOUT", "rechts", "J2.2  DIN Daten 5 V → LED-Modul", 0),
    ("R01", "12V", "rechts", "J2.3  +12 V → LED-Modul", 0),
    ("X03", "GND", "unten", "J3.2  GND ← Netzteil", 790),
    ("X02", "12V", "unten", "J3.1  +12 V ← Netzteil 12 V", 820),
]
XL, XR, XU = 36, 902, 150

for p, netz, richtung, label, yh in EXTERN:
    x, y = pad(p)
    f = FARBE[netz]
    if richtung == "links":
        d, ex, ey, sp = f"M {x} {y} L {XL} {y}", XL, y, 1
        text(XL + 10, y - 8, label, size=9, fill="#222", weight="bold")
    elif richtung == "rechts":
        d, ex, ey, sp = f"M {x} {y} L {XR} {y}", XR, y, -1
        text(XR - 10, y - 8, label, size=9, fill="#222", anchor="end",
             weight="bold")
    else:
        d = f"M {x} {y} L {x} {yh} L {XU} {yh}"
        ex, ey, sp = XU, yh, 1
        text(XU + 10, yh - 8, label, size=9, fill="#222", weight="bold")
    add(f'<path d="{d}" fill="none" stroke="{f}" stroke-width="3.4" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'stroke-dasharray="11 4"/>')
    add(f'<polygon points="{ex},{ey} {ex+9*sp},{ey-4.5} {ex+9*sp},{ey+4.5}" '
        f'fill="{f}"/>')

text(XL, 100, "Kabel nach außen — gestrichelt, bis zum Bildrand:",
     size=9.5, fill="#555", weight="bold")

# -------------------------------------------------------------------- Legende

LX1, LY1, LX2 = 920, 110, 1660
RAHMEN = len(S)
add("")   # Platzhalter, Hoehe steht erst nach dem letzten Eintrag fest
A, B = LX1 + 18, LX1 + 372
text(A, LY1 + 26, "Legende, Raster und Bauteile", size=13, weight="bold",
     fill="#111")

y = LY1 + 48
for c, lbl in [(RED, "+5 V (Agon Pin 4 speist den IC)"),
               (BLK, "GND — gemeinsame Masse"),
               (ORG, "Daten 3,3 V: Agon → Wandler"),
               (YEL, "Daten 5 V: Wandler → Modul"),
               (P12, "12 V — nur rechte untere Ecke"),
               (LEG, "Bauteilbeinchen")]:
    add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" stroke="{c}" '
        f'stroke-width="4" stroke-linecap="round"/>')
    text(A + 38, y + 3.5, lbl, size=9, fill="#333")
    y += 16
add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" stroke="#666" '
    f'stroke-width="3.4" stroke-dasharray="11 4"/>')
text(A + 38, y + 3.5, "Kabel nach außen (bis zum Bildrand)", size=9,
     fill="#333")
y += 20
add(f'<circle cx="{A+14}" cy="{y}" r="7" fill="none" stroke="#2f2a1e" '
    f'stroke-width="1.7"/>')
text(A + 38, y + 3.5, "Pad mit mehreren Litzen", size=9, fill="#333")
y += 20
add(f'<path d="M {A} {y} L {A+9} {y} A 5.5 5.5 0 0 1 {A+20} {y} L {A+28} {y}" '
    f'fill="none" stroke="#666" stroke-width="3"/>')
text(A + 38, y + 3.5, "Bruecke: die Litzen kreuzen sich nur", size=9,
     fill="#333")

y += 26
for n in ["Pad-Namen wie auf der Platine: Reihe A–X, Spalte 18 (links)",
          "bis 01 (rechts). J14 ist also Reihe J, Spalte 14.",
          "Gelötet wird auf der Unterseite; die Litzen dürfen fremde",
          "Löcher überqueren — verbunden ist nur, was am Pad hängt."]:
    text(A, y, n, size=8.5, fill="#555")
    y += 12

y += 10
text(A, y, "Bauteile", size=10, weight="bold", fill="#111")
y += 16
for n in ["IC  SN74AHCT125N, Kerbe links, Pin 1 = M14 (unten links),",
          "      Pin 14 = J14. Optional 14-polige Fassung.",
          "R1  390 Ω in der Datenleitung — Q12 / Q09",
          "R2  8,2 kΩ Pull-down an 1A — Q15 / Q13",
          "C1  100 nF, Stützkondensator — H08 (+5 V) / I08 (GND)",
          "J1  3-polig, Spalte 18: C18 / D18 / E18",
          "J2  3-polig, Spalte 01: P01 / Q01 / R01",
          "J3  2-polig, Reihe X: X02 / X03"]:
    text(A, y, n, size=8.5, fill="#555")
    y += 12

y += 12
text(A, y, "Prüfen vor dem ersten Strom (Durchgangsprüfer)", size=10,
     weight="bold", fill="#8e24aa")
y += 16
for n in ["J3.1 — J2.3 (X02 — R01): 0 Ω, die 12 V gehen durch",
          "J3.1 gegen J1.1, J2.1, J3.2: unendlich — 12 V bleibt allein!",
          "J1.1 — IC Pin 14 (C18 — J14): 0 Ω",
          "J1.3 — IC Pin 1 (E18 — M14): 0 Ω",
          "J1.2 — IC Pin 2 (D18 — M13): 0 Ω",
          "IC Pin 14 — IC Pin 1: > 500 Ω (kein Kurzschluss)",
          "J1.2 — J1.3 über R2: rund 8,2 kΩ"]:
    text(A, y, n, size=8.5, fill="#7a2a24")
    y += 12

Y_LINKS = y

# Verdrahtungsliste
text(B, LY1 + 26, "Verdrahtungsliste — in dieser Reihenfolge löten",
     size=13, weight="bold", fill="#111")
y = LY1 + 48
text(B + 16, y, "von → nach (Pads)", size=8.5, weight="bold", fill="#111")
text(B + 152, y, "Zweck", size=8.5, weight="bold", fill="#111")
y += 14
for i, (netz, pfad, zweck) in enumerate(WIRES, 1):
    add(f'<rect x="{B}" y="{y-7}" width="9" height="9" rx="2" '
        f'fill="{FARBE[netz]}"/>')
    text(B + 16, y, " → ".join(pfad.split()), size=8.5, fill="#333")
    text(B + 152, y, zweck.replace("->", "→"), size=8.5, fill="#555")
    y += 13.5

y += 10
for n in ["Zuletzt die lila 12-V-Litze: sie läuft nur in der rechten",
          "unteren Ecke (X02 → X01 → R01) und berührt nichts anderes.",
          "",
          "Reihenfolge beim Bestücken: 1. Stiftleisten J1–J3 (Pins nach",
          "oben) · 2. IC oder Fassung · 3. C1, R1, R2 · 4. Litzen nach",
          "der Tabelle, kürzeste zuerst · 5. die 12-V-Litze.",
          "",
          "Was die Schaltung tut: Kanal 1 des Vierfach-Puffers hebt das",
          "Datensignal von PC4 (3,3 V) auf 5 V — erst damit erkennen die",
          "SK6812 die Bits sicher. R2 hält 1A auf Masse, solange PC4 nach",
          "dem Reset noch Eingang ist. R1 dämpft Reflexionen auf dem Kabel",
          "zum Modul. Die Kanäle 2–4 bleiben still: ihre OE (Pins 4, 10,",
          "13) liegen an +5 V, ihre Eingänge (5, 9, 12) an GND.",
          "",
          "Die 5 V holt der IC vom Agon (J1.1) — so liegt an seinem",
          "Eingang nie eine Spannung, während er selbst stromlos ist.",
          "Die 12 V des Netzteils berühren die Logik nirgends."]:
    if n:
        text(B, y, n, size=8.5, fill="#555")
    y += 12

LEGENDE_UNTEN = max(y, Y_LINKS, PB - 14) + 14

text(40, 862, "⚠ Lila = 12 V: führt nur in der rechten unteren Ecke "
     "(Spalten 01–02, Reihen R–X) und bleibt von allen 5-V- und "
     "GND-Litzen getrennt. Nie mit Rot oder Schwarz verlöten — 12 V "
     "am IC zerstören ihn und den Agon.", size=10, fill=P12, weight="bold")

S[RAHMEN] = (f'<rect x="{LX1}" y="{LY1}" width="{LX2-LX1}" '
             f'height="{LEGENDE_UNTEN-LY1}" rx="6" fill="#fafafa" '
             f'stroke="#bbb"/>')

add("</svg>")

if "--md" in sys.argv:          # Tabelle fuer docs/AUFBAU-PEGELWANDLER.md
    print("| # | von → nach (Pads) | Netz | Zweck |")
    print("|---|---|---|---|")
    for i, (netz, pfad, zweck) in enumerate(WIRES, 1):
        n = {"+5V": "+5 V", "GND": "GND", "DIN": "Daten 3,3 V",
             "DOUT": "Daten 5 V", "12V": "**12 V**"}[netz]
        print(f"| {i} | `{'` → `'.join(pfad.split())}` | {n} | "
              f"{zweck.replace('->', '→')} |")
    sys.exit(0)

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "bilder", "lochraster-pegelwandler.svg")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(S) + "\n")
print(f"OK {out}  ({len(WIRES)} Litzen, {len(KREUZ)} Kreuzungsstellen, "
      f"{len(FEHLER)} Fehler)")
