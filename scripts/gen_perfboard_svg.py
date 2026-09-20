# -*- coding: utf-8 -*-
"""Erzeugt die Lochraster-Bauplaene fuer den Pegelwandler (docs/bilder/).

Draufsicht auf eine Universal-Lochrasterplatine 5x7 cm mit 18x24 Loechern
(Raster 2,54 mm) und SN74AHCT125N, 390 Ohm, 8,2 kOhm, 100 nF sowie drei
Stiftleisten (J1 Agon, J2 Modul, J3 Netzteil). Elektrisch identisch mit dem
Breadboard-Aufbau aus docs/AUFBAU-PEGELWANDLER.md.

Beschriftung wie auf der Platine des Nutzers:
  Reihen  A (oben) ... X (unten)
  Spalten 18 (links) ... 01 (rechts)
Ein Pad heisst deshalb z. B. "J14" = Reihe J, Spalte 14.

Zwei Varianten, beide mit derselben Schaltung:

  schiene  Litzen laufen rechtwinklig in Reihen und Spalten (Schienen/Bus).
           Jede Verbindung ist eine eigene Litze.
  direkt   Benachbarte Pads werden mit Loetzinn gebrueckt, alles andere
           geht als gerade Litze von Pad zu Pad - so, wie man es mit rotem
           und weissem Klingeldraht baut. Weiss = Masse, rot = alles andere.

Zeichenregeln:
- Die Litzen laufen auf der Loetseite und duerfen fremde Loecher kreuzen;
  verbunden ist nur, was am Pad verloetet ist (dunkle Ringe = Mehrfachpads).
  Kreuzungen werden als Bruecke (Halbbogen) gezeichnet.
- Keine Litze laeuft ueber oder dicht an einem Pad eines fremden Netzes -
  das prueft check_netz() beim Erzeugen und meldet jeden Verstoss.
- Litzen duerfen unter dem IC durchlaufen (sie liegen ja auf der Loetseite);
  dort sind sie blasser gezeichnet.
- Die 12-V-Leitung fuehrt ausschliesslich in der rechten unteren Ecke.
- Kabel nach aussen enden als beschriftete Linien am Bildrand.

Aufruf:  python scripts/gen_perfboard_svg.py            beide Bilder
         python scripts/gen_perfboard_svg.py --md schiene|direkt   Tabellen
"""

import math
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
ZINN = "#cfd2d8"      # Loetzinn-Bruecke
ZINN_R = "#6b6b72"

FARBE = {"+5V": RED, "GND": BLK, "DIN": ORG, "DOUT": YEL, "12V": P12}
# Klingeldraht: weiss ist Masse, rot ist alles andere
KLINGEL = {"GND": "#fdfdfd", "+5V": "#d32f2f", "DIN": "#d32f2f",
           "DOUT": "#d32f2f", "12V": "#d32f2f"}
KLINGEL_NAME = {"GND": "weiß", "+5V": "rot", "DIN": "rot", "DOUT": "rot",
                "12V": "rot"}

W, H = 1680, 900
NCOL, NROW = 18, 24
ROWS = "ABCDEFGHIJKLMNOPQRSTUVWX"
X0, Y0 = 230, 150     # Pad A18 (links oben)
DX, DY = 26, 24       # Raster (nicht massstabsgetreu gezeichnet)
PL, PT = X0 - 28, Y0 - 28
PR, PB = X0 + 17 * DX + 28, Y0 + 23 * DY + 28
HOP = 5.5


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pad(name):
    """'J14' -> (x, y) in Bildkoordinaten."""
    r = ROWS.index(name[0])
    c = int(name[1:])
    return X0 + (NCOL - c) * DX, Y0 + r * DY


def benachbart(a, b):
    """Liegen zwei Pads direkt nebeneinander (waagerecht oder senkrecht)?"""
    ra, ca = ROWS.index(a[0]), int(a[1:])
    rb, cb = ROWS.index(b[0]), int(b[1:])
    return abs(ra - rb) + abs(ca - cb) == 1


def abstand(px, py, x1, y1, x2, y2):
    """Abstand Punkt zu Strecke."""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


# ------------------------------------------------- gemeinsame Bauteile/Pads

IC_OBEN = {14: "J14", 13: "J13", 12: "J12", 11: "J11", 10: "J10",
           9: "J09", 8: "J08"}
IC_UNTEN = {1: "M14", 2: "M13", 3: "M12", 4: "M11", 5: "M10",
            6: "M09", 7: "M08"}
IC_NETZ = {14: "+5V", 13: "+5V", 10: "+5V", 4: "+5V",
           1: "GND", 12: "GND", 9: "GND", 5: "GND", 7: "GND",
           2: "DIN", 3: "DOUT"}

HEADERS = [("J1 → Agon Light 2", ["C18", "D18", "E18"], "v", -26),
           ("J2 → LED-Modul", ["P01", "Q01", "R01"], "v", -24),
           ("J3 ← Netzteil 12 V", ["X03", "X02"], "h", -24)]

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


# ----------------------------------------------------------- Variante schiene

SCHIENE = {
    "name": "schiene",
    "datei": "lochraster-pegelwandler.svg",
    "titel": "Pegelwandler auf Lochraster 5×7 cm — SN74AHCT125N "
             "(Draufsicht, Bauteilseite)",
    "untertitel": "Reihen A–X, Spalten 18 (links) bis 01 (rechts) — "
                  "wie auf der Platine aufgedruckt · Raster 2,54 mm · "
                  "18×24 Löcher · Verdrahtung auf der Lötseite",
    "stil": "netz",
    "wires": [
        ("+5V", "C18 C06", "J1.1 +5 V -> 5-V-Schiene"),
        ("+5V", "C06 P06", "5-V-Schiene (Spalte 06)"),
        ("+5V", "H14 H06", "5-V-Brücke über dem IC (Reihe H)"),
        ("+5V", "J14 H14", "IC Pin 14 VCC"),
        ("+5V", "J13 H13", "IC Pin 13 (OE4) -> VCC"),
        ("+5V", "J10 H10", "IC Pin 10 (OE3) -> VCC"),
        ("+5V", "M11 P11 P06", "IC Pin 4 (OE2) -> VCC"),
        ("GND", "E18 E16 N16", "J1.3 GND -> GND-Bus"),
        ("GND", "N16 N03 P03 P01", "GND-Bus (Reihe N) -> J2.1"),
        ("GND", "M14 N14", "IC Pin 1 (OE1) -> GND"),
        ("GND", "M10 N10", "IC Pin 5 (2A) -> GND"),
        ("GND", "M08 N08", "IC Pin 7 GND"),
        ("GND", "J12 I12 I07 N07", "IC Pin 12 (4A) -> GND"),
        ("GND", "J09 I09", "IC Pin 9 (3A) -> GND"),
        ("GND", "Q15 N15", "R2 (Pull-down) -> GND"),
        ("GND", "X03 X05 N05", "J3.2 GND -> GND-Bus"),
        ("DIN", "D18 D17 R17 R13 M13", "J1.2 PC4 -> IC Pin 2"),
        ("DOUT", "M12 Q12", "IC Pin 3 -> R1"),
        ("DOUT", "Q09 Q01", "R1 -> J2.2 DIN"),
        ("12V", "X02 X01 R01", "J3.1 -> J2.3 (nur Randpfad!)"),
    ],
    "bruecken": [],
    "extra": [("Q12", "DOUT", "R1 Bein 1"), ("Q09", "DOUT", "R1 Bein 2"),
              ("Q15", "GND", "R2 Bein 1"), ("Q13", "DIN", "R2 Bein 2"),
              ("H08", "+5V", "C1 Bein 1"), ("I08", "GND", "C1 Bein 2")],
    "bauteile": [("R1", "Q12", "Q09", "390 Ω",
                  ["#ef6c00", "#ffffff", "#6b3f1d"], "unten", 0, 0),
                 ("R2", "Q15", "Q13", "8,2 kΩ",
                  ["#9e9e9e", "#c62828", "#c62828"], "oben", -18, 0)],
    "c1": ("H08", "I08"),
    "c1_label": (0, -15),
    "pin1_label": ("O14", "middle", 0),
    "warnung": "⚠ Lila = 12 V: führt nur in der rechten unteren Ecke "
               "(Spalten 01–02, Reihen R–X) und bleibt von allen 5-V- und "
               "GND-Litzen getrennt. Nie mit Rot oder Schwarz verlöten — 12 V "
               "am IC zerstören ihn und den Agon.",
    "hinweise": [
        "Pad-Namen wie auf der Platine: Reihe A–X, Spalte 18 (links)",
        "bis 01 (rechts). J14 ist also Reihe J, Spalte 14.",
        "Gelötet wird auf der Unterseite; die Litzen dürfen fremde",
        "Löcher überqueren — verbunden ist nur, was am Pad hängt.",
    ],
    "bauteiltext": [
        "IC  SN74AHCT125N, Kerbe links, Pin 1 = M14 (unten links),",
        "      Pin 14 = J14. Optional 14-polige Fassung.",
        "R1  390 Ω in der Datenleitung — Q12 / Q09",
        "R2  8,2 kΩ Pull-down an 1A — Q15 / Q13",
        "C1  100 nF, Stützkondensator — H08 (+5 V) / I08 (GND)",
        "J1  3-polig, Spalte 18: C18 / D18 / E18",
        "J2  3-polig, Spalte 01: P01 / Q01 / R01",
        "J3  2-polig, Reihe X: X02 / X03",
    ],
    "pruefen": [
        "X02 — R01 (J3.1 — J2.3): 0 Ω, die 12 V gehen durch",
        "X02 gegen C18, P01, X03: unendlich — 12 V bleibt allein!",
        "C18 — J14 (J1.1 — IC Pin 14): 0 Ω",
        "E18 — M14 (J1.3 — IC Pin 1): 0 Ω",
        "D18 — M13 (J1.2 — IC Pin 2): 0 Ω",
        "J14 — M14 (IC Pin 14 — Pin 1): > 500 Ω (kein Kurzschluss)",
        "D18 — E18 (PC4 — GND): rund 8,2 kΩ über R2",
    ],
    "schluss": [
        "Zuletzt die lila 12-V-Litze: sie läuft nur in der rechten",
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
        "Die 12 V des Netzteils berühren die Logik nirgends.",
    ],
}

# ------------------------------------------------------------ Variante direkt

DIREKT = {
    "name": "direkt",
    "datei": "lochraster-pegelwandler-direkt.svg",
    "titel": "Pegelwandler auf Lochraster 5×7 cm — Variante "
             "Klingeldraht (Draufsicht, Bauteilseite)",
    "untertitel": "Benachbarte Pads mit Lötzinn gebrückt, alles andere "
                  "als gerade Litze von Pad zu Pad · weiß = Masse, "
                  "rot = alles andere · Reihen A–X, Spalten 18 (links) "
                  "bis 01 (rechts)",
    "stil": "klingel",
    "wires": [
        ("+5V", "C18 H15", "J1.1 +5 V -> C1 Bein 1"),
        ("+5V", "H15 J14", "C1 Bein 1 -> IC Pin 14"),
        ("+5V", "J10 M11", "IC Pin 10 (OE3) -> Pin 4, unter dem IC"),
        ("+5V", "M11 J13", "IC Pin 4 (OE2) -> Pin 13, unter dem IC"),
        ("GND", "E18 M15", "J1.3 GND -> Stützpunkt neben Pin 1"),
        ("GND", "M15 I16", "GND nach oben, links am IC vorbei"),
        ("GND", "I16 I13", "GND-Knoten über dem IC"),
        ("GND", "H14 I13", "C1 Bein 2 -> GND"),
        ("GND", "I12 I09", "IC Pin 12 (4A) -> Pin 9 (3A)"),
        ("GND", "I09 N08", "IC Pin 9 -> Pin 7, unter dem IC"),
        ("GND", "N08 N10", "IC Pin 7 -> Pin 5 (2A)"),
        ("GND", "P13 N14", "R2 Bein 2 -> GND"),
        ("GND", "P01 N08", "J2.1 GND -> IC Pin 7"),
        ("GND", "X03 N08", "J3.2 GND -> IC Pin 7"),
        ("DIN", "D18 M13", "J1.2 PC4 -> IC Pin 2"),
        ("DOUT", "Q12 Q01", "R1 Bein 2 -> J2.2 DIN"),
        ("12V", "X02 R01", "J3.1 -> J2.3 (nur die Ecke!)"),
    ],
    "bruecken": [
        ("J14", "J13", "+5V", "IC Pin 14 an Pin 13 (OE4)"),
        ("I13", "I12", "GND", "GND-Knoten an den Abzweig von Pin 12"),
        ("I12", "J12", "GND", "Abzweig über IC Pin 12 (4A)"),
        ("I09", "J09", "GND", "Abzweig über IC Pin 9 (3A)"),
        ("M15", "M14", "GND", "Stützpunkt an IC Pin 1 (OE1)"),
        ("M14", "N14", "GND", "IC Pin 1 nach unten abgezweigt"),
        ("M13", "N13", "DIN", "IC Pin 2 an R2 Bein 1"),
        ("M12", "N12", "DOUT", "IC Pin 3 an R1 Bein 1"),
        ("M10", "N10", "GND", "Abzweig unter IC Pin 5 (2A)"),
        ("M08", "N08", "GND", "Abzweig unter IC Pin 7"),
    ],
    "extra": [("N12", "DOUT", "R1 Bein 1"), ("Q12", "DOUT", "R1 Bein 2"),
              ("N13", "DIN", "R2 Bein 1"), ("P13", "GND", "R2 Bein 2"),
              ("H15", "+5V", "C1 Bein 1"), ("H14", "GND", "C1 Bein 2")],
    "bauteile": [("R1", "N12", "Q12", "390 Ω",
                  ["#ef6c00", "#ffffff", "#6b3f1d"], "rechts", 0, 0),
                 ("R2", "N13", "P13", "8,2 kΩ",
                  ["#9e9e9e", "#c62828", "#c62828"], "links", 0, 26)],
    "c1": ("H15", "H14"),
    "c1_label": (36, -18),
    "pin1_label": ("O14", "end", -4),
    "warnung": "⚠ Der lila Kern ist die 12-V-Litze: Sie läuft nur in der "
               "rechten unteren Ecke (X02 → R01) und berührt keine andere "
               "Litze. Nie an ein Pad löten, an dem schon etwas hängt — 12 V "
               "am IC zerstören ihn und den Agon.",
    "hinweise": [
        "Pad-Namen wie auf der Platine: Reihe A–X, Spalte 18 (links)",
        "bis 01 (rechts). J14 ist also Reihe J, Spalte 14.",
        "Benachbarte Pads werden mit Lötzinn verbunden, alles andere",
        "geradewegs mit Klingeldraht von Pad zu Pad.",
        "Gelötet wird auf der Unterseite: Die Litzen dürfen fremde",
        "Löcher und auch das IC überqueren — dort sind sie blass",
        "gezeichnet. Verbunden ist nur, was am Pad verlötet ist.",
    ],
    "bauteiltext": [
        "IC  SN74AHCT125N, Kerbe links, Pin 1 = M14 (unten links),",
        "      Pin 14 = J14. Optional 14-polige Fassung.",
        "R1  390 Ω in der Datenleitung, stehend — N12 / Q12",
        "R2  8,2 kΩ Pull-down an 1A, stehend — N13 / P13",
        "C1  100 nF, ein Loch breit, direkt über dem IC — H15 (+5 V)",
        "      und H14 (GND)",
        "J1  3-polig, Spalte 18: C18 / D18 / E18",
        "J2  3-polig, Spalte 01: P01 / Q01 / R01",
        "J3  2-polig, Reihe X: X02 / X03",
    ],
    "pruefen": [
        "X02 — R01 (J3.1 — J2.3): 0 Ω, die 12 V gehen durch",
        "X02 gegen C18, P01, X03: unendlich — 12 V bleibt allein!",
        "C18 — J14 (J1.1 — IC Pin 14): 0 Ω",
        "E18 — M14 (J1.3 — IC Pin 1): 0 Ω",
        "D18 — M13 (J1.2 — IC Pin 2): 0 Ω",
        "J14 — M14 (IC Pin 14 — Pin 1): > 500 Ω (kein Kurzschluss)",
        "D18 — E18 (PC4 — GND): rund 8,2 kΩ über R2",
        "Jede Lötbrücke mit der Lupe ansehen: Kein Zinn darf auf ein",
        "drittes Pad gelaufen sein — besonders bei J13/J14 am IC.",
    ],
    "schluss": [
        "Zuletzt die 12-V-Litze X02 → R01: sie bleibt in der rechten",
        "unteren Ecke und berührt nichts anderes.",
        "",
        "Reihenfolge: 1. Stiftleisten J1–J3 (Pins nach oben) · 2. IC",
        "oder Fassung · 3. C1, R1, R2 · 4. die Lötzinn-Brücken ·",
        "5. die Litzen von oben nach unten · 6. die 12-V-Litze.",
        "",
        "Klingeldraht ist starr: auf Länge biegen, nur so viel",
        "abisolieren, wie im Pad verschwindet. Die Isolierung soll bis",
        "ans Pad reichen — die Litzen kreuzen einander und laufen",
        "über fremde Löcher.",
        "",
        "Was die Schaltung tut: Kanal 1 des Vierfach-Puffers hebt das",
        "Datensignal von PC4 (3,3 V) auf 5 V — erst damit erkennen die",
        "SK6812 die Bits sicher. R2 hält 1A auf Masse, solange PC4 nach",
        "dem Reset noch Eingang ist. R1 dämpft Reflexionen auf dem Kabel",
        "zum Modul. Die Kanäle 2–4 bleiben still: ihre OE (Pins 4, 10,",
        "13) liegen an +5 V, ihre Eingänge (5, 9, 12) an GND.",
    ],
}

VARIANTEN = {"schiene": SCHIENE, "direkt": DIREKT}


# --------------------------------------------------------------- Netzpruefung

def alle_pads(v):
    """{Pad: Netz} aus Litzen, Bruecken, Bauteilbeinen und IC-Pins."""
    netz = {}
    doppelt = []
    def setze(p, n, wer):
        if netz.setdefault(p, n) != n:
            doppelt.append(f"Pad {p}: {netz[p]} und {n} ({wer})")
    for w in v["wires"]:
        for p in w[1].split():
            setze(p, w[0], "Litze")
    for a, b, n, zweck in v["bruecken"]:
        setze(a, n, "Bruecke")
        setze(b, n, "Bruecke")
    for p, n, _ in v["extra"]:
        setze(p, n, "Bauteil")
    for nr, p in list(IC_OBEN.items()) + list(IC_UNTEN.items()):
        n = IC_NETZ.get(nr)
        if n:
            setze(p, n, f"IC Pin {nr}")
    return netz, doppelt


def segmente(v):
    """[(x1, y1, x2, y2, netz, wire_index)] in Zeichenreihenfolge."""
    out = []
    for i, w in enumerate(v["wires"]):
        ps = w[1].split()
        for a, b in zip(ps, ps[1:]):
            (x1, y1), (x2, y2) = pad(a), pad(b)
            out.append((x1, y1, x2, y2, w[0], i))
    return out


def check_netz(v):
    """Meldet Netzfehler; liefert ausserdem die Zahl der Anschluesse je Pad."""
    netz, fehler = alle_pads(v)
    zahl = {}
    for w in v["wires"]:
        for p in w[1].split():
            zahl[p] = zahl.get(p, 0) + 1
    for p, _, _ in v["extra"]:
        zahl[p] = zahl.get(p, 0) + 1
    for a, b, n, _ in v["bruecken"]:
        if not benachbart(a, b):
            fehler.append(f"Bruecke {a}-{b} liegt nicht nebeneinander")
    for nr, p in list(IC_OBEN.items()) + list(IC_UNTEN.items()):
        if IC_NETZ.get(nr) is None and p in netz:
            fehler.append(f"IC-Pin {nr} ({p}) ist offen, traegt aber etwas")
    for x1, y1, x2, y2, n1, i in segmente(v):
        eigene = set(v["wires"][i][1].split())
        for p, n2 in netz.items():
            if p in eigene:
                continue
            px, py = pad(p)
            d = abstand(px, py, x1, y1, x2, y2)
            if d < 1.0:
                if n1 != n2:
                    fehler.append(f"Litze {n1} ({v['wires'][i][1]}) laeuft "
                                  f"ueber Pad {p} ({n2})")
                else:
                    zahl[p] = zahl.get(p, 0) + 1   # T-Stoss auf dem Pad
            elif d < 9.5 and n1 != n2:
                fehler.append(f"Litze {n1} ({v['wires'][i][1]}) kommt Pad "
                              f"{p} ({n2}) auf {d:.1f} px nahe")
    return fehler, zahl


def kreuzungen(v):
    """{Segment-Index: [(t, x, y)]} - dort wird eine Bruecke gezeichnet."""
    segs = segmente(v)
    out = {}
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            ax1, ay1, ax2, ay2, _, wi = segs[i]
            bx1, by1, bx2, by2, _, wj = segs[j]
            if wi == wj:
                continue
            rx, ry = ax2 - ax1, ay2 - ay1
            sx, sy = bx2 - bx1, by2 - by1
            nenner = rx * sy - ry * sx
            if nenner == 0:
                continue
            t = ((bx1 - ax1) * sy - (by1 - ay1) * sx) / nenner
            u = ((bx1 - ax1) * ry - (by1 - ay1) * rx) / nenner
            if not (0.02 < t < 0.98 and 0.02 < u < 0.98):
                continue
            x, y = ax1 + t * rx, ay1 + t * ry
            a_waag, b_waag = ay1 == ay2, by1 == by2
            if a_waag and not b_waag:
                ziel, tt = i, t
            elif b_waag and not a_waag:
                ziel, tt = j, u
            else:
                ziel, tt = j, u
            out.setdefault(ziel, []).append((tt, x, y))
    return out


def pfad(v, i, kreuz):
    """SVG-Pfad einer Litze, mit Halbbogen an jeder Kreuzung."""
    ps = v["wires"][i][1].split()
    si = 0
    for k in range(i):
        si += len(v["wires"][k][1].split()) - 1
    x, y = pad(ps[0])
    d = [f"M {x:g} {y:g}"]
    for n, (a, b) in enumerate(zip(ps, ps[1:])):
        (x1, y1), (x2, y2) = pad(a), pad(b)
        laenge = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / laenge, (y2 - y1) / laenge
        for t, cx, cy in sorted(kreuz.get(si + n, [])):
            d.append(f"L {cx-HOP*ux:g} {cy-HOP*uy:g}")
            d.append(f"A {HOP} {HOP} 0 0 1 {cx+HOP*ux:g} {cy+HOP*uy:g}")
        d.append(f"L {x2:g} {y2:g}")
    return " ".join(d)


# ------------------------------------------------------------------ Zeichnung

def zeichne(v):
    S = []
    add = S.append

    def text(x, y, t, size=9, fill="#333", anchor="start", weight="normal",
             halo=False):
        h = (' stroke="#ffffff" stroke-width="3" paint-order="stroke"'
             if halo else "")
        add(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{h}>{esc(t)}</text>')

    fehler, zahl = check_netz(v)
    for f in fehler:
        print(f"FEHLER [{v['name']}]: {f}", file=sys.stderr)
    kreuz = kreuzungen(v)

    icx1, icy1 = pad("J14")[0] - 13, pad("J14")[1] + 7
    icx2, icy2 = pad("J08")[0] + 13, pad("M14")[1] - 7

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Arial, sans-serif">')
    add(f'<defs><clipPath id="ic"><rect x="{icx1}" y="{icy1}" '
        f'width="{icx2-icx1}" height="{icy2-icy1}"/></clipPath></defs>')
    add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    text(W / 2, 40, v["titel"], size=17, anchor="middle", weight="bold",
         fill="#111")
    text(W / 2, 64, v["untertitel"], size=10.5, anchor="middle", fill="#666")

    # Platte, Loecher, Rasterbeschriftung
    add(f'<rect x="{PL}" y="{PT}" width="{PR-PL}" height="{PB-PT}" rx="8" '
        f'fill="{BG}" stroke="#8a8264" stroke-width="1.5"/>')
    for r in ROWS:
        for c in range(1, NCOL + 1):
            x, y = pad(f"{r}{c:02d}")
            add(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{DOT}"/>')
    for i, r in enumerate(ROWS):
        y = Y0 + i * DY + 3.5
        if r not in ("C", "D", "E"):
            text(PL - 9, y, r, size=9, fill="#7a7259", anchor="middle",
                 weight="bold")
        if r not in ("P", "Q", "R"):
            text(PR + 9, y, r, size=9, fill="#7a7259", anchor="middle",
                 weight="bold")
    for c in range(1, NCOL + 1):
        x = X0 + (NCOL - c) * DX
        text(x, PT - 9, f"{c:02d}", size=8.5, fill="#7a7259", anchor="middle",
             weight="bold")
        if c not in (2, 3):
            text(x, PB + 15, f"{c:02d}", size=8.5, fill="#7a7259",
                 anchor="middle", weight="bold")
    text((PL + PR) / 2, PT - 26, "18 Löcher = 5 cm", size=9, fill="#888",
         anchor="middle")
    add(f'<text x="{PR+26}" y="{(PT+PB)/2}" font-size="9" fill="#888" '
        f'transform="rotate(90 {PR+26} {(PT+PB)/2})" text-anchor="middle">'
        f'24 Löcher = 7 cm</text>')

    # Litzen (zweimal gebraucht: normal und blass unter dem IC)
    pfade = [(pfad(v, i, kreuz), w[0]) for i, w in enumerate(v["wires"])]

    def male_litzen():
        for d, netz in pfade:
            if v["stil"] == "klingel":
                for farbe, breite in ((ZINN_R, 6.6), (KLINGEL[netz], 5.0),
                                      (FARBE[netz], 1.6)):
                    add(f'<path d="{d}" fill="none" stroke="{farbe}" '
                        f'stroke-width="{breite}" stroke-linecap="round" '
                        f'stroke-linejoin="round"/>')
            else:
                add(f'<path d="{d}" fill="none" stroke="{FARBE[netz]}" '
                    f'stroke-width="3.4" stroke-linecap="round" '
                    f'stroke-linejoin="round"/>')

    male_litzen()

    # Bauteile
    for name, p1, p2, label, bands, lpos, ldx, ldy in v["bauteile"]:
        (x1, y1), (x2, y2) = pad(p1), pad(p2)
        xc, yc = (x1 + x2) / 2, (y1 + y2) / 2
        dreh = f' transform="rotate(90 {xc} {yc})"' if x1 == x2 else ""
        add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LEG}" '
            f'stroke-width="2.5"/>')
        add(f'<rect x="{xc-24}" y="{yc-8}" width="48" height="16" rx="7" '
            f'fill="#e8d5a3" stroke="#8a7a4a"{dreh}/>')
        for k, b in enumerate(bands):
            add(f'<rect x="{xc-15+k*9}" y="{yc-8}" width="4.5" height="16" '
                f'fill="{b}"{dreh}/>')
        lx, ly, anc = xc + ldx, yc + ldy, "middle"
        if lpos == "oben":
            ly -= 16
        elif lpos == "unten":
            ly += 25
        elif lpos == "links":
            lx, anc, ly = lx - 16, "end", ly + 3.5
        else:
            lx, anc, ly = lx + 16, "start", ly + 3.5
        text(lx, ly, f"{name} {label}", size=9, fill="#444", anchor=anc,
             weight="bold", halo=True)

    (cx1, cy1), (cx2, cy2) = pad(v["c1"][0]), pad(v["c1"][1])
    add(f'<line x1="{cx1}" y1="{cy1}" x2="{cx2}" y2="{cy2}" stroke="{LEG}" '
        f'stroke-width="2.5"/>')
    add(f'<circle cx="{(cx1+cx2)/2}" cy="{(cy1+cy2)/2}" r="10" '
        f'fill="#d9a441" stroke="#8a6d1f" stroke-width="1.25"/>')
    text((cx1 + cx2) / 2 + v["c1_label"][0],
         (cy1 + cy2) / 2 + v["c1_label"][1], "C1 100 nF", size=9, fill="#444",
         anchor="middle", weight="bold", halo=True)

    # IC; darunter laufende Litzen blass wiederholen
    for nr, p in list(IC_OBEN.items()) + list(IC_UNTEN.items()):
        x, y = pad(p)
        add(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{icy1 if nr >= 8 else icy2}"'
            f' stroke="{LEG}" stroke-width="3"/>')
    add(f'<rect x="{icx1}" y="{icy1}" width="{icx2-icx1}" '
        f'height="{icy2-icy1}" rx="4" fill="#2b2b2b" stroke="#111"/>')
    add('<g clip-path="url(#ic)" opacity="0.42">')
    male_litzen()
    add('</g>')
    add(f'<path d="M {icx1} {(icy1+icy2)/2-8} A 8 8 0 0 0 {icx1} '
        f'{(icy1+icy2)/2+8}" fill="{BG}" stroke="#111" stroke-width="1"/>')
    for nr, p in IC_OBEN.items():
        text(pad(p)[0], icy1 + 14, str(nr), size=9.5, fill="#fff",
             anchor="middle", weight="bold")
    for nr, p in IC_UNTEN.items():
        text(pad(p)[0], icy2 - 6, str(nr), size=9.5,
             fill=("#ff8a80" if nr == 1 else "#fff"), anchor="middle",
             weight="bold")
    text((icx1 + icx2) / 2, (icy1 + icy2) / 2 + 4, "SN74AHCT125N", size=10,
         fill="#9e9e9e", anchor="middle")
    x, y = pad("M14")
    add(f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{RED}" '
        f'stroke-width="1.8"/>')
    lp, lanc, ldx = v["pin1_label"]
    text(pad(lp)[0] + ldx, pad(lp)[1] + 4, "Pin 1", size=9, fill=RED,
         anchor=lanc, weight="bold", halo=True)

    # Loetbruecken
    for a, b, netz, _ in v["bruecken"]:
        (x1, y1), (x2, y2) = pad(a), pad(b)
        for farbe, breite in ((ZINN_R, 12), (ZINN, 9)):
            add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{farbe}" stroke-width="{breite}" '
                f'stroke-linecap="round"/>')

    # Pads, Mehrfachpads
    for p, n in sorted(zahl.items()):
        x, y = pad(p)
        add(f'<circle cx="{x}" cy="{y}" r="4.2" fill="#5d564044"/>')
        if n >= 2:
            add(f'<circle cx="{x}" cy="{y}" r="6.6" fill="none" '
                f'stroke="#2f2a1e" stroke-width="1.7"/>')

    # Stiftleisten
    for titel, pads, richtung, dy in HEADERS:
        xs = [pad(p)[0] for p in pads]
        ys = [pad(p)[1] for p in pads]
        if richtung == "v":
            bx = (min(xs) - 13) if min(xs) < W / 3 else (max(xs) + 4)
            add(f'<rect x="{bx}" y="{min(ys)-12}" width="9" '
                f'height="{max(ys)-min(ys)+24}" rx="2.5" fill="#37474f" '
                f'stroke="#111"/>')
        else:
            add(f'<rect x="{min(xs)-12}" y="{max(ys)+4}" '
                f'width="{max(xs)-min(xs)+24}" height="9" rx="2.5" '
                f'fill="#37474f" stroke="#111"/>')
        for p in pads:
            px, py = pad(p)
            add(f'<rect x="{px-6}" y="{py-6}" width="12" height="12" rx="2" '
                f'fill="#cfd8dc" stroke="#111" stroke-width="1.2"/>')
        text((min(xs) + max(xs)) / 2, min(ys) + dy, titel, size=10,
             fill="#111", anchor="middle", weight="bold", halo=True)

    # Kabel nach aussen
    for p, netz, richtung, label, yh in EXTERN:
        px, py = pad(p)
        f = FARBE[netz]
        if richtung == "links":
            d, ex, ey, sp = f"M {px} {py} L {XL} {py}", XL, py, 1
            text(XL + 10, py - 8, label, size=9, fill="#222", weight="bold")
        elif richtung == "rechts":
            d, ex, ey, sp = f"M {px} {py} L {XR} {py}", XR, py, -1
            text(XR - 10, py - 8, label, size=9, fill="#222", anchor="end",
                 weight="bold")
        else:
            d, ex, ey, sp = f"M {px} {py} L {px} {yh} L {XU} {yh}", XU, yh, 1
            text(XU + 10, yh - 8, label, size=9, fill="#222", weight="bold")
        add(f'<path d="{d}" fill="none" stroke="{f}" stroke-width="3.4" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'stroke-dasharray="11 4"/>')
        add(f'<polygon points="{ex},{ey} {ex+9*sp},{ey-4.5} '
            f'{ex+9*sp},{ey+4.5}" fill="{f}"/>')
    text(XL, 100, "Kabel nach außen — gestrichelt, bis zum Bildrand:",
         size=9.5, fill="#555", weight="bold")

    # ---------------------------------------------------------------- Legende
    LX1, LY1, LX2 = 920, 110, 1660
    rahmen = len(S)
    add("")
    A, B = LX1 + 18, LX1 + 372
    text(A, LY1 + 26, "Legende, Raster und Bauteile", size=13, weight="bold",
         fill="#111")
    y = LY1 + 48
    if v["stil"] == "klingel":
        for farbe, lbl in ((KLINGEL["+5V"], "roter Klingeldraht: +5 V, Daten "
                            "und 12 V"),
                           (KLINGEL["GND"], "weißer Klingeldraht: immer "
                            "Masse")):
            add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" '
                f'stroke="{ZINN_R}" stroke-width="6.6" '
                f'stroke-linecap="round"/>')
            add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" '
                f'stroke="{farbe}" stroke-width="5" stroke-linecap="round"/>')
            text(A + 38, y + 3.5, lbl, size=9, fill="#333")
            y += 17
        text(A, y + 3, "Der dünne Kern zeigt das Netz:", size=9,
             fill="#333")
        y += 16
        for netz, lbl in (("+5V", "+5 V"), ("GND", "GND"),
                          ("DIN", "Daten 3,3 V"), ("DOUT", "Daten 5 V"),
                          ("12V", "12 V")):
            add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" '
                f'stroke="{ZINN_R}" stroke-width="6.6" '
                f'stroke-linecap="round"/>')
            add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" '
                f'stroke="{KLINGEL[netz]}" stroke-width="5" '
                f'stroke-linecap="round"/>')
            add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" '
                f'stroke="{FARBE[netz]}" stroke-width="1.6" '
                f'stroke-linecap="round"/>')
            text(A + 38, y + 3.5, lbl, size=9, fill="#333")
            y += 15
        add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" stroke="{ZINN_R}" '
            f'stroke-width="12" stroke-linecap="round"/>')
        add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" stroke="{ZINN}" '
            f'stroke-width="9" stroke-linecap="round"/>')
        text(A + 38, y + 3.5, "Lötzinn-Brücke zwischen zwei "
             "Nachbarpads", size=9, fill="#333")
        y += 20
    else:
        for c, lbl in ((RED, "+5 V (Agon Pin 4 speist den IC)"),
                       (BLK, "GND — gemeinsame Masse"),
                       (ORG, "Daten 3,3 V: Agon → Wandler"),
                       (YEL, "Daten 5 V: Wandler → Modul"),
                       (P12, "12 V — nur rechte untere Ecke"),
                       (LEG, "Bauteilbeinchen")):
            add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" stroke="{c}" '
                f'stroke-width="4" stroke-linecap="round"/>')
            text(A + 38, y + 3.5, lbl, size=9, fill="#333")
            y += 16
    add(f'<line x1="{A}" y1="{y}" x2="{A+28}" y2="{y}" stroke="#666" '
        f'stroke-width="3.4" stroke-dasharray="11 4"/>')
    text(A + 38, y + 3.5, "Kabel nach außen (bis zum Bildrand)", size=9,
         fill="#333")
    y += 20
    add(f'<circle cx="{A+14}" cy="{y}" r="6.6" fill="none" stroke="#2f2a1e" '
        f'stroke-width="1.7"/>')
    text(A + 38, y + 3.5, "Pad mit mehreren Anschlüssen", size=9,
         fill="#333")
    y += 20
    add(f'<path d="M {A} {y} L {A+9} {y} A 5.5 5.5 0 0 1 {A+20} {y} '
        f'L {A+28} {y}" fill="none" stroke="#666" stroke-width="3"/>')
    text(A + 38, y + 3.5, "Brücke: die Litzen kreuzen sich nur", size=9,
         fill="#333")
    y += 26
    for n in v["hinweise"]:
        if n:
            text(A, y, n, size=8.5, fill="#555")
        y += 12

    y += 10
    text(A, y, "Bauteile", size=10, weight="bold", fill="#111")
    y += 16
    for n in v["bauteiltext"]:
        text(A, y, n, size=8.5, fill="#555")
        y += 12

    y += 12
    text(A, y, "Prüfen vor dem ersten Strom (Durchgangsprüfer)",
         size=10, weight="bold", fill="#8e24aa")
    y += 16
    for n in v["pruefen"]:
        text(A, y, n, size=8.5, fill="#7a2a24")
        y += 12
    y_links = y

    # rechte Spalte: Bruecken und Litzen
    y = LY1 + 26
    if v["bruecken"]:
        text(B, y, "1. Lötzinn-Brücken (Pads nebeneinander)",
             size=13, weight="bold", fill="#111")
        y += 22
        for i, (a, b, netz, zweck) in enumerate(v["bruecken"], 1):
            add(f'<rect x="{B}" y="{y-7}" width="9" height="9" rx="2" '
                f'fill="{FARBE[netz]}"/>')
            text(B + 16, y, f"{a} – {b}", size=8.5, fill="#333")
            text(B + 100, y, zweck, size=8.5, fill="#555")
            y += 13.5
        y += 12
        text(B, y, "2. Litzen — in dieser Reihenfolge löten",
             size=13, weight="bold", fill="#111")
        y += 22
    else:
        text(B, y, "Verdrahtungsliste — in dieser Reihenfolge löten",
             size=13, weight="bold", fill="#111")
        y += 22
    klingel = v["stil"] == "klingel"
    xpad = B + 50 if klingel else B + 16
    if klingel:
        text(B + 16, y, "Draht", size=8.5, weight="bold", fill="#111")
    text(xpad, y, "von → nach (Pads)", size=8.5, weight="bold", fill="#111")
    text(B + 168, y, "Zweck", size=8.5, weight="bold", fill="#111")
    y += 14
    for netz, pfd, zweck in v["wires"]:
        add(f'<rect x="{B}" y="{y-7}" width="9" height="9" rx="2" '
            f'fill="{FARBE[netz]}"/>')
        if klingel:
            text(B + 16, y, KLINGEL_NAME[netz], size=8.5, fill="#333")
        text(xpad, y, " → ".join(pfd.split()), size=8.5, fill="#333")
        text(B + 168, y, zweck.replace("->", "→"), size=8.5, fill="#555")
        y += 13.5
    y += 10
    for n in v["schluss"]:
        if n:
            text(B, y, n, size=8.5, fill="#555")
        y += 12

    unten = max(y, y_links, PB - 14) + 14
    S[rahmen] = (f'<rect x="{LX1}" y="{LY1}" width="{LX2-LX1}" '
                 f'height="{unten-LY1}" rx="6" fill="#fafafa" '
                 f'stroke="#bbb"/>')

    text(40, 862, v["warnung"], size=10, fill=P12, weight="bold")
    add("</svg>")
    return S, len(kreuz), fehler


def md_tabelle(v):
    zeilen = []
    if v["bruecken"]:
        zeilen.append("| # | Pads | Netz | Zweck |")
        zeilen.append("|---|---|---|---|")
        for i, (a, b, netz, zweck) in enumerate(v["bruecken"], 1):
            zeilen.append(f"| B{i} | `{a}` – `{b}` | {NETZNAME[netz]} | "
                          f"{zweck} |")
        zeilen.append("")
    kopf = "| # | Draht | von → nach (Pads) | Zweck |" \
        if v["stil"] == "klingel" else "| # | von → nach (Pads) | Netz | Zweck |"
    zeilen.append(kopf)
    zeilen.append("|---|---|---|---|")
    for i, (netz, pfd, zweck) in enumerate(v["wires"], 1):
        pads = "` → `".join(pfd.split())
        spalte2 = KLINGEL_NAME[netz] if v["stil"] == "klingel" \
            else NETZNAME[netz]
        if v["stil"] == "klingel":
            zeilen.append(f"| {i} | {spalte2} | `{pads}` | "
                          f"{zweck.replace('->', chr(8594))} |")
        else:
            zeilen.append(f"| {i} | `{pads}` | {spalte2} | "
                          f"{zweck.replace('->', chr(8594))} |")
    return "\n".join(zeilen)


NETZNAME = {"+5V": "+5 V", "GND": "GND", "DIN": "Daten 3,3 V",
            "DOUT": "Daten 5 V", "12V": "**12 V**"}


def main():
    if "--md" in sys.argv:
        name = sys.argv[sys.argv.index("--md") + 1]
        print(md_tabelle(VARIANTEN[name]))
        return
    ziel = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "docs", "bilder")
    os.makedirs(ziel, exist_ok=True)
    for v in VARIANTEN.values():
        S, nkreuz, fehler = zeichne(v)
        out = os.path.join(ziel, v["datei"])
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(S) + "\n")
        print(f"OK {out}  ({len(v['wires'])} Litzen, "
              f"{len(v['bruecken'])} Bruecken, {nkreuz} Kreuzungsstellen, "
              f"{len(fehler)} Fehler)")


main()
