; ===================================================================
;  SK6812 / WS2812 Ausgaberoutine fuer Agon Light 2
;  Datenleitung: PC4 = Pin 21 des 34-poligen Headers
;
;  Assemblieren auf dem Agon:
;     /bin/ez80asm ws2812.asm ws2812.bin -oB0000 -a1
;
;  Aufruf aus BBC BASIC:
;     *LOAD ws2812.bin &B0000
;     CALL &B0004                 : REM einmalig, PC4 auf Ausgang
;     !(&B0008) = fb%             : REM Framebuffer (GRBW)
;     !(&B000C) = buf%            : REM Bitpuffer, 8 * p_rep Byte je fb-Byte
;     !(&B0010) = 576             : REM Anzahl Framebuffer-Bytes
;     ?(&B0014) = 2               : REM LEDs je Eintrag (Vorgabe 2)
;     ?(&B0015) = 255             : REM Helligkeit 0-255 (Vorgabe 255)
;     CALL &B0000                 : REM Frame ausgeben
;
;  LEDs je Eintrag: Die Lumanode-Wand hat 2 LEDs je Pixel, 288 LEDs an
;  der Kette. Die beiden LEDs eines Pixels folgen in der Kette immer
;  direkt aufeinander (LED 2k und 2k+1, geprueft an der ledPairs-Tabelle
;  der Arduino-Firmware). Der Framebuffer haelt deshalb nur 144 Eintraege,
;  und die Routine sendet jeden p_rep-mal. Der Bitpuffer braucht
;  8 * p_rep Byte je Framebuffer-Byte, bei 144 Eintraegen also 9216 Byte.
;
;  Helligkeit: Beim Entpacken laeuft jedes Byte durch eine Tabelle, die
;  hoechstens MAXB liefert. Das ist die Strombremse. Sie sitzt hier,
;  weil jeder Frame diesen Weg nimmt, egal welches BASIC-Programm ihn
;  erzeugt. MAXB = 90 gilt fuer alle vier Kanaele: 4 x 90 = 360 ist
;  dasselbe Budget wie die Arduino-Firmware mit 3 x 120 (RGB, W immer 0).
;  Siehe docs/PLAN.md, Abschnitt 5.
;
;  Zur Ladeadresse: &B0000 ist laut MOS-Dokumentation der Bereich fuer
;  von SD geladene Star-Command-Programme (Moslets). BASIC laesst sein
;  HIMEM bei &B0000 und nicht absenken, deshalb ist das der einzige
;  feste Platz, der nicht mit BASIC kollidiert. Solange waehrend des
;  Betriebs kein Moslet aus /mos/ gestartet wird, bleibt der Code
;  unangetastet. Das aufrufende Programm prueft vor jedem Frame, ob
;  bei &B0000 noch $C3 steht, und laedt sonst nach.
;
;  Siehe docs/PLAN.md, Abschnitt 2 und 11.
; ===================================================================
;
;  Zeitrechnung, eZ80 @ 18,432 MHz, ein Takt = 54,25 ns.
;  Zyklen laut eZ80 CPU User Manual UM0077:
;     nop 1, out (bc),r 3, ld r,(hl) 2, inc rr 1, ld r,n 2,
;     xor r 1, dec rr 1, or r 1, jr cc,d 3 genommen / 2 sonst
;
;  Ablauf je Bit, t = Takt seit Beginn des Blocks:
;     ld a,$10      2      t=0..1
;     out (bc),a    3      t=2..4    -> Pin HIGH ab t=5
;     ld a,(hl)     2      t=5..6
;     inc hl        1      t=7
;     out (bc),a    3      t=8..10   -> Pin = Bitwert ab t=11
;     nop nop       2      t=11..12
;     xor a         1      t=13
;     out (bc),a    3      t=14..16  -> Pin LOW ab t=17
;     dec de        1      t=17      Schleifenlogik statt Fuell-NOPs
;     ld a,d        1      t=18
;     or e          1      t=19
;     jr nz         3      t=20..22
;                          naechstes Bit ab t=23
;
;     T0H = 11-5 =  6 Takte = 325 ns   (Soll 300 +/- 150)
;     T1H = 17-5 = 12 Takte = 651 ns   (Soll 600 +/- 150)
;     Periode    = 23 Takte = 1248 ns  (Soll 1250)
;
;  Die vier Befehle der Bitschleife brauchen zusammen genau die sechs
;  Takte, die sonst mit NOPs zu fuellen waeren. Die Schleife laeuft
;  dadurch voellig gleichmaessig - es gibt keine Naht zwischen Bytes.
;
;  Sollte sich auf echter Hardware zeigen, dass I/O-Wartezyklen das
;  Timing verschieben, wird ausschliesslich die Anzahl der NOPs
;  angepasst - die Struktur bleibt.
;
;  Achtung: out (bc),a schreibt den ganzen Port C. Die anderen PC-Pins
;  duerfen deshalb keine Ausgaenge sein, die einen Pegel halten sollen.
; ===================================================================

    .assume adl=1
    .org $B0000

MAXB:       .equ 90             ; Obergrenze je Kanal nach der Tabelle
LUT:        .equ $B0800         ; 256 Byte Helligkeitstabelle, liegt
                                ; hinter dem Code im Moslet-Bereich

; ---- Einsprungtabelle und Parameterblock -------------------------
entry:      jp   send           ; $B0000  Frame ausgeben
initentry:  jp   gpioinit       ; $B0004  PC4 auf Ausgang schalten
p_src:      .db  0,0,0,0        ; $B0008  Framebuffer-Adresse
p_dst:      .db  0,0,0,0        ; $B000C  Bitpuffer-Adresse
p_len:      .db  0,0,0,0        ; $B0010  Anzahl Framebuffer-Bytes
p_rep:      .db  2              ; $B0014  LEDs je Eintrag
p_bri:      .db  255            ; $B0015  Helligkeit 0-255
            .db  0,0            ; $B0016  frei

; ---- PC4 als digitalen Ausgang konfigurieren ---------------------
; Mode 1 (Ausgang) verlangt DDR=0, ALT1=0 und ALT2=0 fuer das Bit.
; Die uebrigen Bits von Port C bleiben unberuehrt.
gpioinit:
    ld   bc, $009F              ; PC_DDR
    in   a, (c)
    and  $EF                    ; Bit 4 loeschen -> Ausgang
    out  (c), a
    ld   bc, $00A0              ; PC_ALT1
    in   a, (c)
    and  $EF
    out  (c), a
    ld   bc, $00A1              ; PC_ALT2
    in   a, (c)
    and  $EF
    out  (c), a
    ld   bc, $009E              ; PC_DR: Pin auf Low
    in   a, (c)
    and  $EF
    out  (c), a
    ret

; ---- Helligkeitstabelle aufbauen ---------------------------------
; LUT[v] = v * k / 256 mit k = p_bri * MAXB / 256. Bei p_bri = 255
; ist k = 89 und LUT[255] = 88 - also nie ueber MAXB.
; Wird vor jedem Frame neu gebaut (256 Runden, rund 0,2 ms), damit
; eine geaenderte Helligkeit ohne eigenen Aufruf wirkt.
buildlut:
    ld   a, (p_bri)
    ld   b, a
    ld   c, MAXB
    mlt  bc                     ; BC = p_bri * MAXB
    ld   e, b                   ; k = oberes Byte
    ld   hl, LUT
    ld   d, 0                   ; v = 0..255
bl1:
    ld   b, d
    ld   c, e
    mlt  bc                     ; BC = v * k
    ld   (hl), b
    inc  hl
    inc  d
    jr   nz, bl1
    ret

; ---- Frame ausgeben ----------------------------------------------
send:
    push ix
    push iy
    call buildlut

; Schritt 1: Framebuffer in den Bitpuffer entpacken.
; Je Datenbit ein Byte, das bereits das fertige Portmuster enthaelt
; ($10 oder $00). Das haelt die zeitkritische Schleife frei von
; Schiebe- und Maskierarbeit. Jeder Eintrag (4 Byte GRBW) wird p_rep-
; mal hintereinander entpackt, jedes Byte vorher durch die Tabelle.
    ld   hl, (p_src)
    ld   de, (p_dst)
    ld   bc, (p_len)
    srl  b                      ; BC / 4 = Anzahl Eintraege
    rr   c
    srl  b
    rr   c
    ld   a, b
    or   c
    jr   z, sendend             ; nichts zu tun
expled:
    push bc                     ; Eintrags-Zaehler retten
    ld   a, (p_rep)
    or   a
    jr   nz, reptok
    inc  a                      ; p_rep = 0 wie 1 behandeln
reptok:
    ld   b, a
exprep:
    push bc                     ; Wiederholungs-Zaehler
    push hl                     ; Anfang des Eintrags
    ld   b, 4                   ; G, R, B, W
expbyte:
    push bc
    ld   a, (hl)
    inc  hl
    push hl
    ld   hl, LUT                ; C = LUT[A]
    ld   bc, 0
    ld   c, a
    add  hl, bc
    ld   c, (hl)
    pop  hl
    ld   b, 8
expbit:
    rl   c                      ; MSB zuerst -> Carry
    sbc  a, a                   ; Carry -> $FF bzw. $00
    and  $10                    ; -> Portmuster fuer PC4
    ld   (de), a
    inc  de
    djnz expbit
    pop  bc
    djnz expbyte
    pop  hl                     ; zurueck an den Anfang des Eintrags
    pop  bc
    djnz exprep
    ld   bc, 4                  ; weiter zum naechsten Eintrag
    add  hl, bc
    pop  bc
    dec  bc
    ld   a, b
    or   c
    jr   nz, expled

; Schritt 2: Bitpuffer zeitgenau ausgeben.
; Anzahl Bits = Ende des Bitpuffers - Anfang, damit sie immer zu dem
; passt, was Schritt 1 tatsaechlich geschrieben hat.
; Ab hier sind Interrupts gesperrt. Ein Interrupt vom VDP oder der
; Tastatur wuerde den Bitstrom zerreissen und die Kette verfaerben.
; Bei 288 LEDs sind das 9216 Bits, also rund 11,5 ms.
    ex   de, hl                 ; HL = Ende des Bitpuffers
    ld   de, (p_dst)
    or   a
    sbc  hl, de
    ex   de, hl                 ; DE = Bitzaehler
    ld   hl, (p_dst)
    ld   bc, $009E              ; PC_DR, ab hier unveraendert
    di

sendbit:
    ld   a, $10                 ; 2   Portmuster High
    out  (c), a                 ; 3   -> Pin HIGH ab t=5
    ld   a, (hl)                ; 2   vorbereitetes Bitmuster
    inc  hl                     ; 1
    out  (c), a                 ; 3   -> Pin = Bitwert ab t=11
    nop                         ; 1
    nop                         ; 1
    xor  a                      ; 1   Portmuster Low
    out  (c), a                 ; 3   -> Pin LOW ab t=17
    dec  de                     ; 1   diese vier Befehle stehen
    ld   a, d                   ; 1   genau an der Stelle der sonst
    or   e                      ; 1   noetigen sechs Fuell-NOPs
    jr   nz, sendbit            ; 3   Summe: 23 Takte

; Schritt 3: Latch. Die Kette uebernimmt die Daten erst nach einer
; Low-Phase: SK6812 > 80 us, neuere WS2812B > 280 us. 1000 Durchlaeufe
; a 6 Takte sind rund 325 us. Der Pin ist nach dem letzten Bit bereits
; low, Interrupts koennen die Pause nur verlaengern - deshalb duerfen
; sie hier schon wieder an.
    ei
    ld   de, 1000
latch:
    dec  de
    ld   a, d
    or   e
    jr   nz, latch

sendend:
    pop  iy
    pop  ix
    ld   hl, 0
    ret
