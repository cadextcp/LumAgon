"""Schreibt eine Datei ueber USB auf die SD-Karte im Agon - ohne Umstecken.

    python scripts/agonload.py DATEI [ZIEL] [--port COM7] [--am-mos-prompt] [--kein-neustart]

ZIEL ist der Pfad auf der Karte OHNE fuehrenden Schraegstrich (Git Bash
wuerde ihn sonst in einen Windows-Pfad umwandeln), etwa progs/start.bas.
Ohne ZIEL: progs/<Dateiname>.

Ablauf:
 1. Den Agon zum MOS-Prompt bringen: ESC, aus start.bas mit "0" in BASIC,
    mit *BYE ins MOS. Mit --am-mos-prompt entfaellt das.
 2. "hexload vdp /progs/agonload.tmp" eintippen. hexload.bin (in /mos der
    Karte) laesst den VDP Intel-HEX-Zeilen von USB empfangen, legt die Daten
    ab &40000 in den Speicher und schreibt sie danach als Datei.
 3. Die Datei als Intel HEX senden, im erweiterten Format von send.py
    (agon-hexload): jede Zeile mit CRC16, die der VDP beantwortet; fehlerhafte
    Zeilen gehen erneut hinaus; am Ende prueft der VDP eine CRC32 ueber alles.
 4. Nur wenn CRC32 und Bytezahl stimmen: altes ZIEL loeschen, die temporaere
    Datei umbenennen. hexload loescht seine Zieldatei naemlich schon vor dem
    Schreiben, auch bei einem Abbruch - ein Fehlschlag darf ZIEL deshalb nie
    direkt treffen (eine kaputte ws2812.bin legt den Autostart lahm).
 5. BASIC und start.bas wieder starten. Mit --kein-neustart entfaellt das.

Warum der MOS-Prompt: hexload legt die Daten ab &40000 ab, dort laeuft BBC
BASIC. hexload selbst laeuft ab &B0000 und ueberschreibt die geladene
ws2812.bin; start.bas laedt sie beim Start ohnehin neu.

Voraussetzung: Konsolenmodus an (autoexec.txt), sonst kommen die getippten
Befehle nicht an. Braucht nur pyserial.

Nachgebaut nach send.py von Jeroen Venema (agon-hexload, MIT-Lizenz) und
hexload.h der VDP-Firmware.
"""

import argparse
import re
import sys
import threading
import time
import zlib
from pathlib import Path

import serial

from agonmon import BAUD, clean, find_port

LOAD_ADDRESS = 0x040000     # Standardadresse von hexload
LINE_BYTES = 128            # Datenbytes je HEX-Zeile
TEMP = "progs/agonload.tmp"


def crc16(data):
    """CRC16 wie im VDP: Polynom 0x8005, Start 0, nicht gespiegelt (CRC-16/BUYPASS)."""
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x8005) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def hex_record(rectype, addr16, payload):
    body = bytes([len(payload), (addr16 >> 8) & 0xFF, addr16 & 0xFF, rectype]) + payload
    return ":" + (body + bytes([(-sum(body)) & 0xFF])).hex().upper()


def build_records(data, crc32):
    """Startsatz (erweitertes Format mit CRC32), Daten ab LOAD_ADDRESS, Endsatz."""
    recs = [hex_record(0xFF, 0, bytes([0, 0]) + crc32.to_bytes(4, "big"))]
    upper, pos = None, 0
    while pos < len(data):
        addr = LOAD_ADDRESS + pos
        if upper != addr >> 16:
            upper = addr >> 16
            recs.append(hex_record(0x04, 0, upper.to_bytes(2, "big")))
        n = min(LINE_BYTES, len(data) - pos, 0x10000 - (addr & 0xFFFF))
        recs.append(hex_record(0x00, addr & 0xFFFF, data[pos:pos + n]))
        pos += n
    recs.append(hex_record(0x01, 0, b""))
    return recs


class Link:
    """Serielle Verbindung zum VDP mit mitlaufendem Empfangspuffer."""

    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.port, self.ser.baudrate, self.ser.timeout = port, BAUD, 0.05
        self.ser.dtr = False        # sonst setzt der Wandler den ESP32 zurueck
        self.ser.rts = False
        self.ser.open()
        self.buf = bytearray()
        self.stop = threading.Event()
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        while not self.stop.is_set():
            d = self.ser.read(512)
            if d:
                self.buf.extend(d)

    def close(self):
        self.stop.set()
        time.sleep(0.1)
        self.ser.close()

    def mark(self):
        return len(self.buf)

    def text(self, since):
        return clean(self.buf[since:])

    def wait_text(self, pattern, since, timeout):
        pat, t0 = re.compile(pattern), time.time()
        while time.time() - t0 < timeout:
            m = pat.search(self.text(since))
            if m:
                return m
            time.sleep(0.05)
        return None

    def wait_bytes(self, expected, since, timeout):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if expected in self.buf[since:]:
                return True
            time.sleep(0.005)
        return False

    def type(self, s, cr=True):
        """Wie getippt: Zeichen einzeln, der Konsolenmodus macht Tasten daraus."""
        for c in (s + ("\r" if cr else "")).encode("latin-1"):
            self.ser.write(bytes([c]))
            time.sleep(0.03)
        time.sleep(0.3)

    def command(self, s, wait=1.5):
        m = self.mark()
        self.type(s)
        time.sleep(wait)
        return self.text(m)


MOS_PROMPT = r"\*$"                  # MOS-Prompt, z. B. "/progs *"


def to_mos_prompt(link):
    """Aus start.bas oder BASIC zum MOS-Prompt. Jeder Schritt wird bestaetigt -
    sonst landen Befehle als Tastendruecke im Menue von start.bas."""
    state = None
    for _ in range(3):              # ESC kann waehrend LED-Ausgabe verloren gehen
        m = link.mark()
        link.type("\x1b", cr=False)
        hit = link.wait_text(r"Bereit - Taste|Escape", m, 4)
        if hit:
            state = hit.group(0)
            break
    if state is None:               # keine Antwort: vielleicht schon am MOS-Prompt
        m = link.mark()
        link.type("")
        if link.wait_text(MOS_PROMPT, m, 2):
            return
        raise RuntimeError("Agon reagiert weder als start.bas noch als BASIC noch als MOS")
    if state == "Bereit - Taste":
        time.sleep(1.2)             # Bereit-Melodie abwarten; ESC hat den Tastenpuffer geleert
        m = link.mark()
        link.type("0", cr=False)
        if not link.wait_text(r"Ende - zurueck zu BASIC[\s\S]*>", m, 6):
            raise RuntimeError("start.bas reagiert nicht auf '0'")
    m = link.mark()
    link.type("*BYE")
    if not link.wait_text(MOS_PROMPT, m, 5):
        raise RuntimeError("MOS-Prompt nach *BYE nicht erreicht")


def release(link):
    """Endsatz senden, damit VDP und hexload nach einem Fehler nicht haengen bleiben.
    hexload schreibt dann hoechstens die temporaere Datei."""
    eof = hex_record(0x01, 0, b"").encode("ascii")
    m = link.mark()
    link.ser.write(eof + f"{crc16(eof):04X}".encode("ascii"))
    link.wait_text(r"bytes|File error", m, 5)


def send_file(link, data, temp):
    crc32 = zlib.crc32(data)
    recs = build_records(data, crc32)
    m = link.mark()
    link.type(f"hexload vdp /{temp}")
    # Der VDP meldet seinen Empfangsmodus (im Konsolenmodus sichtbar). Ohne diese
    # Meldung geht kein einziges HEX-Zeichen hinaus - es wuerde sonst getippt.
    if not link.wait_text(r"Receiving Intel HEX records", m, 5):
        raise RuntimeError(f"hexload startet nicht: {link.text(m).strip()!r}")
    time.sleep(0.2)
    try:
        _send_records(link, data, recs, crc32)
    except RuntimeError:
        release(link)
        raise


def _send_records(link, data, recs, crc32):
    t0 = time.time()
    for i, rec in enumerate(recs):
        line = rec.encode("ascii")
        want = crc16(line)
        for attempt in range(5):
            m = link.mark()
            link.ser.write(line + f"{want:04X}".encode("ascii"))
            if link.wait_bytes(want.to_bytes(2, "little"), m, 1.0):
                break
            if i == 0:
                raise RuntimeError("VDP antwortet nicht auf den Startsatz - kein erweitertes "
                                   "Hexload im VDP, oder hexload lief nicht an. Empfangen: "
                                   + repr(bytes(link.buf[m:])[-80:]))
            print(f"  Zeile {i}: keine gueltige Antwort, Versuch {attempt + 2}")
        else:
            raise RuntimeError(f"Zeile {i} nach 5 Versuchen nicht angekommen")
        if i == len(recs) - 1:
            end_mark = m
        elif i % 16 == 0:
            print(f"  {i}/{len(recs)} Zeilen")
    if not link.wait_bytes(crc32.to_bytes(4, "little"), end_mark, 3):
        raise RuntimeError("CRC32 vom VDP fehlt oder falsch - Datei nicht uebernommen")
    m = link.wait_text(r"(\d+) bytes|File error", end_mark, 8)
    if not m or m.group(0) == "File error" or int(m.group(1)) != len(data):
        raise RuntimeError(f"hexload meldet: {m.group(0) if m else 'nichts'} (erwartet {len(data)} bytes)")
    print(f"  {len(recs)} Zeilen, {len(data)} Byte, CRC32 {crc32:08X} ok, {time.time() - t0:.1f} s")


def replace_target(link, temp, target):
    out = link.command(f"DELETE /{target}", wait=1.5)
    if re.search(r"\(Y|\?", out):   # Rueckfrage mancher MOS-Versionen
        link.command("Y", wait=1.0)
    out = link.command(f"RENAME /{temp} /{target}", wait=1.5)
    if re.search(r"rror|Invalid|not found", out):
        raise RuntimeError(f"Umbenennen gescheitert: {out.strip()}")


def main():
    ap = argparse.ArgumentParser(description="Datei per USB auf die SD-Karte im Agon")
    ap.add_argument("datei")
    ap.add_argument("ziel", nargs="?", help="Pfad auf der Karte ohne fuehrenden /, Vorgabe progs/<Name>")
    ap.add_argument("--port", help="z. B. COM7; ohne Angabe automatisch suchen")
    ap.add_argument("--am-mos-prompt", action="store_true", help="Agon steht schon am MOS-Prompt")
    ap.add_argument("--kein-neustart", action="store_true", help="danach nicht start.bas starten")
    a = ap.parse_args()

    src = Path(a.datei)
    data = src.read_bytes()
    target = (a.ziel or f"progs/{src.name}").replace("\\", "/")
    if ":" in target or target.startswith("/"):
        sys.exit(f"ZIEL '{target}' sieht nach einem Windows-Pfad aus - ohne fuehrenden / angeben, "
                 "z. B. progs/start.bas (Git Bash wandelt /... um).")
    if not data:
        sys.exit("Leere Datei - nichts zu senden.")

    link = Link(a.port or find_port())
    try:
        if not a.am_mos_prompt:
            print("Agon zum MOS-Prompt ...")
            to_mos_prompt(link)
        print(f"Sende {src} -> /{target} ...")
        send_file(link, data, TEMP)
        replace_target(link, TEMP, target)
        print(f"/{target} geschrieben.")
        if not a.kein_neustart:
            link.command("LOAD /bin/bbcbasic24.bin", wait=1.0)
            m = link.mark()
            link.type("RUN . /progs/start.bas")
            ok = link.wait_text(r"Bereit", m, 15)
            print("start.bas laeuft wieder." if ok else "start.bas meldet sich nicht - bitte Reset.")
    except RuntimeError as e:
        print("FEHLER:", e)
        print("Die Zieldatei ist unveraendert. Agon steht vermutlich am MOS-Prompt.")
        print("--- Mitschnitt der Sitzung (Ende) ---")
        print(link.text(0)[-2000:])
        sys.exit(1)
    finally:
        link.close()


if __name__ == "__main__":
    main()
