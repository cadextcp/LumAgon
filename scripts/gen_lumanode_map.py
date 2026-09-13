"""Erzeugt sdcard/progs/matrix.map fuer die Lumanode-12x12-Wand.

Quelle der Tabelle: ledPairs[12][12][2] aus der Arduino-Firmware der Wand
(lumanode/build_lumanode_ha.py). Dort wurde sie 1:1 aus dem Pixel-Builder-
Plan uebernommen und am echten Aufbau korrigiert. Werte 1-basiert, je Pixel
zwei LEDs, 288 LEDs insgesamt.

Die zwei LEDs eines Pixels liegen in der Kette immer direkt hintereinander
(0-basiert 2k und 2k+1). Das prueft dieses Skript. Deshalb genuegt je Pixel
ein Paar-Index k = 0..143; ws2812.asm sendet jeden Framebuffer-Eintrag
zweimal (p_rep = 2).

Format matrix.map (wie calib.bas): Byte 0 Breite, Byte 1 Hoehe, danach je
Position ein Byte Paar-Index, zeilenweise von oben links.

Aufruf:  python scripts/gen_lumanode_map.py
"""

import re
from pathlib import Path

# 1:1 aus der Firmware kopiert - bei einem Umbau der Wand hier ersetzen.
LED_PAIRS_C = """
 {{43,44},{41,42},{53,54},{51,52},{139,140},{137,138},{149,150},{147,148},{235,236},{233,234},{245,246},{243,244}},
 {{45,46},{47,48},{55,56},{49,50},{141,142},{143,144},{151,152},{145,146},{237,238},{239,240},{247,248},{241,242}},
 {{33,34},{39,40},{61,62},{59,60},{129,130},{135,136},{157,158},{155,156},{225,226},{231,232},{253,254},{251,252}},
 {{35,36},{37,38},{63,64},{57,58},{131,132},{133,134},{159,160},{153,154},{227,228},{229,230},{255,256},{249,250}},
 {{25,26},{31,32},{69,70},{67,68},{121,122},{127,128},{165,166},{163,164},{217,218},{223,224},{261,262},{259,260}},
 {{27,28},{29,30},{71,72},{65,66},{123,124},{125,126},{167,168},{161,162},{219,220},{221,222},{263,264},{257,258}},
 {{17,18},{23,24},{77,78},{75,76},{113,114},{119,120},{173,174},{171,172},{209,210},{215,216},{269,270},{267,268}},
 {{19,20},{21,22},{79,80},{73,74},{115,116},{117,118},{175,176},{169,170},{211,212},{213,214},{271,272},{265,266}},
 {{9,10},{15,16},{85,86},{83,84},{89,90},{95,96},{181,182},{179,180},{185,186},{191,192},{277,278},{275,276}},
 {{11,12},{13,14},{87,88},{81,82},{91,92},{93,94},{183,184},{177,178},{187,188},{189,190},{279,280},{273,274}},
 {{1,2},{7,8},{99,100},{97,98},{105,106},{111,112},{195,196},{193,194},{201,202},{207,208},{285,286},{283,284}},
 {{3,4},{5,6},{101,102},{103,104},{107,108},{109,110},{197,198},{199,200},{203,204},{205,206},{287,288},{281,282}}
"""

WIDTH = HEIGHT = 12


def parse(text):
    rows = [r for r in text.strip().splitlines() if r.strip()]
    return [[(int(a), int(b)) for a, b in re.findall(r"\{(\d+),(\d+)\}", r)] for r in rows]


def main():
    table = parse(LED_PAIRS_C)
    assert len(table) == HEIGHT and all(len(r) == WIDTH for r in table), "Tabelle ist nicht 12x12"
    leds = sorted(i for r in table for p in r for i in p)
    assert leds == list(range(1, WIDTH * HEIGHT * 2 + 1)), "nicht jede LED genau einmal"
    for y, row in enumerate(table):
        for x, (a, b) in enumerate(row):
            assert b == a + 1 and a % 2 == 1, f"Pixel {x},{y}: LEDs {a},{b} sind kein Kettenpaar"

    pairs = [[(a - 1) // 2 for a, _ in row] for row in table]
    out = Path(__file__).resolve().parent.parent / "sdcard" / "progs" / "matrix.map"
    out.write_bytes(bytes([WIDTH, HEIGHT] + [k for row in pairs for k in row]))

    print(f"{out} geschrieben ({out.stat().st_size} Byte). Paar-Index je Position:")
    for row in pairs:
        print(" ".join(f"{k:3d}" for k in row))


if __name__ == "__main__":
    main()
