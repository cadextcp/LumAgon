; ===================================================================
;  Zyklen-Messung fuer den eZ80 des Agon
;
;  Zweck: klaeren, ob die Zyklenangaben aus dem eZ80 User Manual
;  (UM0077) der tatsaechlichen Ausfuehrung entsprechen, oder ob
;  Wartezyklen fuer Speicherzugriffe hinzukommen. Davon haengt ab,
;  ob sich SK6812-Bitbanging ueberhaupt zyklengenau auslegen laesst.
;
;     /bin/ez80asm cyctest.asm cyctest.bin -oB0000 -a1
;     *LOAD cyctest.bin &B0000
;     !(&B0008) = <Anzahl Durchlaeufe>
;     CALL &B0000   Leerschleife,     laut Manual  6 Takte je Runde
;     CALL &B0004   Schleife mit OUT, laut Manual 12 Takte je Runde
;
;  Bei 18,432 MHz entspricht ein Takt 54,25 ns. Aus der gemessenen
;  Zeit je Runde ergibt sich der reale Takt-Faktor.
; ===================================================================

    .assume adl=1
    .org $B0000

entry1:     jp   plainloop      ; $B0000
entry2:     jp   outloop        ; $B0004
p_cnt:      .db  0,0,0,0        ; $B0008  Anzahl Durchlaeufe

; ---- Referenzschleife ohne Speicher- und I/O-Zugriff --------------
; dec de 1 + ld a,d 1 + or e 1 + jr nz 3 = 6 Takte je Runde
plainloop:
    ld   de, (p_cnt)
    di
pl1:
    dec  de
    ld   a, d
    or   e
    jr   nz, pl1
    ei
    ld   hl, 0
    ret

; ---- Schleife mit drei I/O-Zugriffen, wie in der Bitausgabe ------
; ld a,n 2 + out 3 + out 3 + out 3 = 11, plus 6 Schleife = 17,
; abzueglich der drei eingesparten NOPs -> Vergleichswert 17 Takte.
; Geschrieben wird auf PC_DR, aber nur Bit 4; sind die Pins nicht
; als Ausgang geschaltet, bleibt das ohne Wirkung nach aussen.
outloop:
    ld   de, (p_cnt)
    ld   bc, $009E
    di
ol1:
    ld   a, $10
    out  (c), a
    xor  a
    out  (c), a
    out  (c), a
    dec  de
    ld   a, d
    or   e
    jr   nz, ol1
    ei
    ld   hl, 0
    ret
