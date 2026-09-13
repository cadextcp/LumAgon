"""Steuert den echten Agon ueber USB - fuer Tests, auch durch Agenten.

    python scripts/agonctl.py [--port COM7] [--timeout S] [--raw] ENDE-REGEX EINGABE ...

Eingaben wie bei emutest.py:
  "@WAIT:re"   warten, bis neue Ausgabe (ab dem letzten Senden) auf re passt
  "@SLEEP:s"   Pause in Sekunden
  "@KEY:x"     Zeichen ohne CR senden (Python-Escapes erlaubt, z. B. \\x1b)
  sonst        Zeile + CR senden
Zeichen gehen einzeln mit 30 ms Abstand hinaus, wie getippt.

Wartemuster so waehlen, dass sie nicht schon im Echo der getippten Zeile
stehen (etwa 'CHK [0-9]+' statt 'CHK'), und erst tippen, wenn der Agon am
Prompt ist: Tasten, die waehrend einer Rechnung ankommen, und die erste
Taste direkt nach ESC in start.bas gehen verloren.

Voraussetzung: Der Konsolenmodus des VDP ist an (autoexec.txt und start.bas
schalten ihn ein). Dann kommt jede Ausgabe ueber USB an, und gesendete
Zeichen landen beim Agon wie Tastendruecke. Der Port darf nicht gleichzeitig
von agonmon.py belegt sein.

Beispiele (Agon wartet im Menue von start.bas):
  LEDs aus:
    python scripts/agonctl.py "LEDs aus" "@KEY:3"
  start.bas beenden und eine BASIC-Zeile ausfuehren:
    python scripts/agonctl.py "MCTL=" "@KEY:0" "@SLEEP:3" 'PRINT "MCTL=";GET(&C4)'
  Programmzeile auf dem Agon aendern und speichern (ohne SD umzustecken):
    python scripts/agonctl.py "Bereit" "@KEY:0" "@SLEEP:3" \\
        '1330 PROCpause(ms% DIV 10+4)' 'SAVE "/progs/start.bas"' "@SLEEP:2" RUN

Achtung: Waehrend die LED-Routine Frames ausgibt, gehen Tastendruecke
teilweise verloren (docs/PLAN.md, Abschnitt 8) - wichtige Tasten wie "0"
dann mehrfach senden.

Rueckgabewert 0, wenn ENDE-REGEX in der Ausgabe auftauchte, sonst 1.
"""

import argparse
import re
import sys
import threading
import time

import serial

from agonmon import BAUD, clean, find_port


def main():
    ap = argparse.ArgumentParser(description="Agon ueber USB fernsteuern")
    ap.add_argument("--port", help="z. B. COM7; ohne Angabe automatisch suchen")
    ap.add_argument("--timeout", type=float, default=60, help="Sekunden je Warteschritt")
    ap.add_argument("--raw", action="store_true", help="die letzten Rohbytes mit ausgeben")
    ap.add_argument("until", help="Regex, bei dem der Lauf fertig ist")
    ap.add_argument("items", nargs="*", help="Eingaben, siehe Modulbeschreibung")
    a = ap.parse_args()

    ser = serial.Serial()
    ser.port, ser.baudrate, ser.timeout = a.port or find_port(), BAUD, 0.1
    ser.dtr = False          # sonst setzt der USB-Seriell-Wandler den ESP32 zurueck
    ser.rts = False
    ser.open()
    raw = bytearray()
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            d = ser.read(512)
            if d:
                raw.extend(d)

    threading.Thread(target=reader, daemon=True).start()
    time.sleep(0.5)
    mark = 0
    for it in a.items:
        if it.startswith("@WAIT:"):
            pat, t1 = re.compile(it[6:]), time.time()
            while time.time() - t1 < a.timeout and not pat.search(clean(raw[mark:])):
                time.sleep(0.2)
            continue
        if it.startswith("@SLEEP:"):
            time.sleep(float(it[7:]))
            continue
        if it.startswith("@KEY:"):
            data = it[5:].encode("latin-1").decode("unicode_escape").encode("latin-1")
        else:
            data = (it + "\r").encode("latin-1")
        mark = len(raw)
        for c in data:
            ser.write(bytes([c]))
            time.sleep(0.03)
        time.sleep(0.3)

    until = re.compile(a.until)
    t0 = time.time()
    while time.time() - t0 < a.timeout and not until.search(clean(raw)):
        time.sleep(0.2)
    time.sleep(0.5)
    stop.set()
    ser.close()
    found = bool(until.search(clean(raw)))
    print(clean(raw).replace("\a", ""))
    if a.raw:
        print("=== ROH (letzte 300 Byte):", bytes(raw[-300:]))
    print("=== ENDMARKE", "GEFUNDEN" if found else "NICHT GEFUNDEN (Timeout)", "===")
    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()
