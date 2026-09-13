"""Treibt den Agon-CLI-Emulator ohne Fenster: Eingaben senden, auf Ausgaben warten.

    python scripts/emutest.py [--sd PFAD] [--mos DATEI] [--timeout S] ENDE-REGEX EINGABE ...

EINGABE:
  "@WAIT:re"   warten, bis neue Ausgabe (ab dem letzten Senden) auf re passt
  "@SLEEP:s"   Pause in Sekunden
  "@KEY:x"     Zeichen ohne CR senden (Python-Escapes erlaubt, z. B. \\x1b)
  sonst        Zeile + CR senden

--mos waehlt eine andere Firmware, relativ zum Emulator-Ordner, etwa
firmware/mos_platform.bin (MOS 3) oder firmware/mos_quark.bin (MOS 1.04).
Ohne Angabe laeuft Console8 MOS 2.3.3.

Beispiele (sdcard/autoexec.txt startet start.bas; nach "Bereit" fuehrt die
Zeile "0" von dort in den BASIC-Prompt):

  ws2812.bin bauen:
    python scripts/emutest.py "Done in" "@WAIT:Bereit" "0" "@SLEEP:3" "*BYE" \\
        "LOAD /bin/ez80asm.bin" "RUN . ws2812.asm ws2812.bin -oB0000 -a1"
  Selbsttest der Ausgaberoutine:
    python scripts/emutest.py "wstest: " "@WAIT:Bereit" "0" "@SLEEP:3" \\
        'LOAD "wstest.bas"' RUN

Git Bash wandelt Argumente, die mit "/" beginnen, in Windows-Pfade um
("/bin/ez80asm" wird zu "C:/Program Files/Git/usr/bin/ez80asm"). Deshalb
bauen die Beispiele mit "LOAD /bin/..." und "RUN ." - das laeuft zudem unter
jeder MOS-Version. Sonst: MSYS_NO_PATHCONV=1 voranstellen.

Eigenheiten des CLI-Emulators (Fab Agon Emulator 1.2.4):
- die erste Eingabezeile geht beim Booten verloren -> zwei Leerzeilen voran
- endet stdin, beendet er sich sofort -> dieses Skript haelt stdin offen
- Zeichen ohne CR kommen bei GET nicht an; jede Zeile liefert CR und LF,
  also zwei Tastendruecke - Menues deshalb lieber am Geraet testen
- MODE blockiert (Fake-VDP) -> nur Programmteile ohne Grafik testen
- er zaehlt keine echten eZ80-Zyklen; Timing ist nur am Geraet pruefbar

Rueckgabewert 0, wenn ENDE-REGEX in der Ausgabe auftauchte, sonst 1.
"""

import argparse
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EMU_DIR = REPO / "tools" / "fab-agon-emulator-v1.2.4-windows-x64"


def main():
    ap = argparse.ArgumentParser(description="Agon-CLI-Emulator fernsteuern")
    ap.add_argument("--sd", default=str(REPO / "sdcard"), help="SD-Karten-Ordner")
    ap.add_argument("--mos", help="andere MOS-Firmware, relativ zum Emulator-Ordner")
    ap.add_argument("--timeout", type=float, default=120, help="Sekunden je Warteschritt")
    ap.add_argument("until", help="Regex, bei dem der Lauf fertig ist")
    ap.add_argument("items", nargs="*", help="Eingaben, siehe Modulbeschreibung")
    a = ap.parse_args()

    exe = EMU_DIR / "agon-cli-emulator.exe"
    if not exe.exists():
        sys.exit("Emulator fehlt - siehe README, 'Einrichtung auf einem neuen Rechner'.")
    cmd = [str(exe), "-u", "--sdcard", a.sd] + (["--mos", a.mos] if a.mos else [])
    p = subprocess.Popen(cmd, cwd=EMU_DIR, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = []

    def reader():
        for chunk in iter(lambda: p.stdout.read1(4096), b""):
            out.append(chunk.replace(b"\0", b"").decode("latin-1"))

    def text():
        return "".join(out)

    threading.Thread(target=reader, daemon=True).start()
    time.sleep(3)                                  # Boot und autoexec abwarten
    mark = 0
    for it in a.items:
        if it.startswith("@WAIT:"):
            pat, t1 = re.compile(it[6:]), time.time()
            while time.time() - t1 < a.timeout and not pat.search(text()[mark:]):
                time.sleep(0.3)
            continue
        if it.startswith("@SLEEP:"):
            time.sleep(float(it[7:]))
            continue
        if it.startswith("@KEY:"):
            data = it[5:].encode("latin-1").decode("unicode_escape").encode("latin-1")
        else:
            data = (it + "\r\n").encode("latin-1")
        mark = len(text())
        p.stdin.write(data)
        p.stdin.flush()
        time.sleep(1.5)

    until = re.compile(a.until)
    t0 = time.time()
    while time.time() - t0 < a.timeout and not until.search(text()):
        time.sleep(0.5)
    time.sleep(1)
    p.kill()
    found = bool(until.search(text()))
    sys.stdout.reconfigure(errors="replace")
    print(text())
    print("=== ENDMARKE", "GEFUNDEN" if found else "NICHT GEFUNDEN (Timeout)", "===")
    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()
