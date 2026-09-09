"""Spielt den Projektstand auf die SD-Karte des Agon (im Kartenleser des PCs).

    python scripts/deploy_sd.py H:              kopieren und pruefen
    python scripts/deploy_sd.py H: --dry-run    nur anzeigen, was passieren wuerde

Kopiert sdcard/autoexec.txt ins Wurzelverzeichnis der Karte und alle Dateien
aus sdcard/progs/ nach /progs (inklusive des gebauten ws2812.bin) und prueft
danach jede Datei per Pruefsumme. Weicht eine vorhandene autoexec.txt ab und
gibt es noch keine autoexec.alt, wird sie zuerst als autoexec.alt gesichert.

Nie angefasst werden MOS.bin, firmware.bin (Flash-Images) und alle anderen
Ordner der Karte.

Ohne Umstecken geht es per USB mit scripts/agonload.py (eine Datei je
Aufruf, Karte bleibt im Agon). Dieses Skript ist fuer den Fall, dass der
Konsolenmodus nicht laeuft, oder fuer eine frisch eingerichtete Karte.

ws2812.bin ist nicht im Repo, es wird gebaut - siehe scripts/emutest.py.
Danach die Karte in Windows "auswerfen" und in den Agon stecken.
"""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC_AUTOEXEC = REPO / "sdcard" / "autoexec.txt"
SRC_PROGS = REPO / "sdcard" / "progs"


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Projektstand auf die Agon-SD-Karte")
    ap.add_argument("target", help="Laufwerk oder Ordner der SD-Karte, z. B. H:")
    ap.add_argument("--dry-run", action="store_true", help="nichts schreiben")
    a = ap.parse_args()

    root = Path(a.target + "\\" if a.target.endswith(":") else a.target)
    if not root.is_dir():
        sys.exit(f"{root} nicht gefunden - steckt die Karte im Kartenleser?")

    binfile, asmfile = SRC_PROGS / "ws2812.bin", SRC_PROGS / "ws2812.asm"
    if not binfile.exists():
        sys.exit("ws2812.bin fehlt - erst im Emulator assemblieren (scripts/emutest.py).")
    if binfile.stat().st_mtime < asmfile.stat().st_mtime:
        sys.exit("ws2812.bin ist aelter als ws2812.asm - erst neu assemblieren.")

    plan = [(SRC_AUTOEXEC, root / "autoexec.txt")]
    plan += [(f, root / "progs" / f.name) for f in sorted(SRC_PROGS.iterdir()) if f.is_file()]

    old = root / "autoexec.txt"
    backup = root / "autoexec.alt"
    if old.exists() and md5(old) != md5(SRC_AUTOEXEC) and not backup.exists():
        print(f"sichere {old} -> {backup}")
        if not a.dry_run:
            shutil.copy2(old, backup)

    for src, dst in plan:
        state = "neu" if not dst.exists() else ("gleich" if md5(dst) == md5(src) else "ersetzt")
        print(f"{state:8} {dst}")
        if not a.dry_run and state != "gleich":
            dst.parent.mkdir(exist_ok=True)
            shutil.copy2(src, dst)

    if a.dry_run:
        print("Probelauf - nichts geschrieben.")
        return
    bad = [dst for src, dst in plan if md5(src) != md5(dst)]
    if bad:
        sys.exit("Pruefsumme stimmt nicht: " + ", ".join(map(str, bad)))
    print(f"{len(plan)} Dateien geprueft, alles gleich. Karte jetzt auswerfen.")


if __name__ == "__main__":
    main()
