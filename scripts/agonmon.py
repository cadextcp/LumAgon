"""Terminal fuer den Agon Light 2 ueber USB - fuer den Betrieb ohne Bildschirm.

autoexec.txt und start.bas schalten den Konsolenmodus des VDP ein
(VDU 23,0,&FE,1, ab VDP 1.04). Dann spiegelt der VDP alle Ausgaben auf
seinen USB-Anschluss und reicht Tasten, die hier getippt werden, an MOS
weiter - wie eine zweite Tastatur. Der Agon muss dafuer per USB-C am PC
haengen, derselbe Anschluss, ueber den er Strom bekommt.

    python scripts/agonmon.py          Port automatisch suchen
    python scripts/agonmon.py COM7     Port vorgeben

Strg+] beendet. Braucht pyserial (pip install pyserial).

Der Konsolenmodus spiegelt die rohen VDU-Bytes. Steuerbytes werden hier
ausgefiltert; die Parameter mancher VDU-Befehle (etwa der Toene) koennen
trotzdem als einzelne Zeichen wie "<" durchrutschen.

DTR und RTS bleiben aus: Der USB-Seriell-Wandler des Agon Light 2 kann
darueber den ESP32 zuruecksetzen (Auto-Reset zum Flashen), und ein
zurueckgesetzter VDP vergisst den Konsolenmodus.
"""

import sys
import threading

import serial
from serial.tools import list_ports

try:
    import msvcrt
except ImportError:          # ausserhalb von Windows: nur mithoeren
    msvcrt = None

BAUD = 115200  # SERIALBAUDRATE der Console8-VDP-Firmware
KNOWN_VIDS = {0x1A86: "CH340", 0x10C4: "CP210x", 0x0403: "FTDI"}
QUIT = "\x1d"  # Strg+]


def find_port():
    ports = list(list_ports.comports())
    candidates = [p for p in ports if p.vid in KNOWN_VIDS] or ports
    if len(candidates) == 1:
        return candidates[0].device
    print("Kein eindeutiger Port gefunden. Vorhanden:")
    for p in ports:
        print(f"  {p.device}  {p.description}")
    if not ports:
        print("  (keiner - haengt der Agon per USB-C am PC?)")
    sys.exit("Port angeben, z. B.: python scripts/agonmon.py COM7")


def clean(data):
    """Nur Text, Zeilenumbrueche und Tab durchlassen; die Glocke als \\a."""
    out = []
    for b in data:
        if b == 10 or 32 <= b < 127:
            out.append(chr(b))
        elif b == 9:
            out.append("\t")
        elif b == 7:
            out.append("\a")
    return "".join(out)


def reader(ser, stop):
    while not stop.is_set():
        data = ser.read(256)
        if data:
            sys.stdout.write(clean(data))
            sys.stdout.flush()


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    ser = serial.Serial()
    ser.port, ser.baudrate, ser.timeout = port, BAUD, 0.1
    ser.dtr = False
    ser.rts = False
    ser.open()
    stop = threading.Event()
    threading.Thread(target=reader, args=(ser, stop), daemon=True).start()
    print(f"Verbunden mit {port} ({BAUD} Baud) - Strg+] beendet.")
    try:
        while True:
            if msvcrt is None:
                stop.wait(1)
                continue
            ch = msvcrt.getwch()
            if ch == QUIT:
                break
            if ch in ("\x00", "\xe0"):   # Sondertasten (Pfeile, F-Tasten) auslassen
                msvcrt.getwch()
                continue
            ser.write(ch.encode("latin-1", "ignore"))
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        ser.close()
        print("\nBeendet.")


if __name__ == "__main__":
    main()
