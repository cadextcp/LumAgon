   10 REM ================================================================
   20 REM  Startprogramm fuer den Betrieb ohne Bildschirm
   30 REM
   40 REM  autoexec.txt startet es direkt. Rueckmeldung kommt ueber den
   50 REM  Kopfhoerer; haengt ein PC per USB am Agon, zeigt
   60 REM  scripts/agonmon.py dort alle Texte und nimmt Tasten an.
   70 REM
   80 REM  Tasten im Menue:
   90 REM    2        Dauertest: Farbwechsel, jede Taste klickt, 0 beendet
  100 REM    3        alle LEDs aus
  110 REM    0        Ende, zurueck zu BASIC
  120 REM    jede andere Taste  LED-Test (laeuft von selbst durch)
  130 REM  ESC bricht jederzeit ab und fuehrt zurueck ins Menue.
  140 REM
  150 REM  Toene:
  160 REM    aufsteigend C-E-G     bereit, wartet auf eine Taste
  170 REM    hoher Doppelpiep      Taste erkannt, es geht los
  180 REM    n kurze Pieps         Schritt n beginnt
  190 REM    Klick                 naechster Pixel / Taste erkannt
  200 REM    absteigend G-E-C      fertig oder abgebrochen
  210 REM    drei tiefe Toene      Fehler
  220 REM ================================================================
  230 :
  240 VDU 23,0,254,1 : REM Konsolenmodus: Texte und Tasten auch ueber USB
  250 vol%=60 : np%=144 : ch%=1
  260 DIM fb% np%*4-1
  270 DIM bf% np%*64-1
  280 ok%=FALSE
  290 ON ERROR PROCfehler : IF ok% THEN 350 ELSE END
  300 PRINT "LED-Wand, Start ohne Bildschirm"
  310 OSCLI("LOAD ws2812.bin &B0000")
  320 CALL &B0004 : ok%=TRUE
  330 PROCaus
  340 PROCbereit
  350 REPEAT
  360   k%=GET
  370   IF k%=48 THEN PROCende
  380   IF k%=50 THEN PROCstart : PROCdauer
  390   IF k%=51 THEN PROCstart : PROCaus : PRINT "LEDs aus"
  400   IF k%<>50 AND k%<>51 THEN PROCstart : PROCledtest
  410   PROCbereit
  420 UNTIL FALSE
  430 :
  440 REM ---- LED-Test: laeuft von selbst, jede Taste springt weiter ----
  450 DEF PROCledtest
  460 LOCAL i%,q%
  470 PRINT "LED-Test"
  480 PROCschritt(1) : PRINT "1 Pixel 0 rot" : PROCeins(60,0,0,0)
  490 PROCschritt(2) : PRINT "2 Pixel 0 gruen" : PROCeins(0,60,0,0)
  500 PROCschritt(3) : PRINT "3 Pixel 0 blau" : PROCeins(0,0,60,0)
  510 PROCschritt(4) : PRINT "4 Pixel 0 weiss (W-Kanal)" : PROCeins(0,0,0,60)
  520 PROCschritt(5) : PRINT "5 Pixel 0 bis 3 nacheinander"
  530 FOR i%=0 TO 3
  540   PROCclear : PROCset(i%,45,45,45,0) : PROCsend
  550   PROCklick
  560   q%=INKEY(100)
  570 NEXT
  580 PROCschritt(6) : PRINT "6 alle schwach weiss - bunt heisst: Timing falsch"
  590 PROCclear
  600 FOR i%=0 TO np%-1 : PROCset(i%,24,24,24,0) : NEXT
  610 PROCsend
  620 q%=INKEY(500)
  630 PROCaus
  640 PRINT "LED-Test fertig"
  650 PROCfertig
  660 ENDPROC
  670 :
  680 DEF PROCeins(r%,g%,b%,w%)
  690 LOCAL q%
  700 PROCclear : PROCset(0,r%,g%,b%,w%) : PROCsend
  710 q%=INKEY(300)
  720 ENDPROC
  730 :
  740 REM ---- Dauertest: viele Frames, prueft die Tastatur waehrenddessen
  750 REM Jeder Frame sperrt die Interrupts rund 11,5 ms. Klickt jede
  760 REM Taste, gehen keine Tastendruecke verloren (docs/PLAN.md, Abschn. 8).
  770 DEF PROCdauer
  780 LOCAL h%,n%,f%,q%,t%,c%,i%
  790 PRINT "Dauertest - jede Taste klickt, 0 beendet"
  800 h%=0 : n%=0 : f%=0 : t%=TIME : q%=-1
  810 REPEAT
  820   IF (f% AND 7)=0 THEN c%=FNfarbe(h%) : h%=(h%+3) MOD 255 : FOR i%=0 TO np%*4-4 STEP 4 : !(fb%+i%)=c% : NEXT
  830   PROCsend : f%=f%+1
  840   q%=INKEY(0)
  850   IF q%>=0 AND q%<>48 THEN n%=n%+1 : PROCklick
  860   IF TIME-t%>=1000 THEN t%=TIME : PRINT "  ";f%;" Frames, ";n%;" Tasten"
  870 UNTIL q%=48
  880 PROCaus
  890 PRINT "Dauertest: ";f%;" Frames, ";n%;" Tasten"
  900 PROCfertig
  910 ENDPROC
  920 :
  930 REM Farbkreis in drei Abschnitten, h% von 0 bis 254.
  940 REM Ergebnis als Wort in der Bytefolge G,R,B,W.
  950 DEF FNfarbe(h%)
  960 LOCAL r%,g%,b%,s%
  970 s%=(h% MOD 85)*3
  980 IF h%<85 THEN r%=255-s% : g%=s% : b%=0
  990 IF h%>=85 AND h%<170 THEN r%=0 : g%=255-s% : b%=s%
 1000 IF h%>=170 THEN r%=s% : g%=0 : b%=255-s%
 1010 =g%+r%*256+b%*65536
 1020 :
 1030 REM ---- LED-Ausgabe ------------------------------------------------
 1040 REM Framebuffer G,R,B,W je Pixel; ws2812.bin sendet jeden Eintrag
 1050 REM zweimal (2 LEDs je Pixel) und begrenzt jeden Kanal auf 90.
 1060 DEF PROCset(i%,r%,g%,b%,w%)
 1070 LOCAL o%
 1080 o%=fb%+i%*4
 1090 ?o%=g% : ?(o%+1)=r% : ?(o%+2)=b% : ?(o%+3)=w%
 1100 ENDPROC
 1110 :
 1120 DEF PROCclear
 1130 LOCAL i%
 1140 FOR i%=0 TO np%*4-4 STEP 4 : !(fb%+i%)=0 : NEXT
 1150 ENDPROC
 1160 :
 1170 DEF PROCaus
 1180 PROCclear : PROCsend
 1190 ENDPROC
 1200 :
 1210 DEF PROCsend
 1220 IF ?&B0000<>&C3 THEN OSCLI("LOAD ws2812.bin &B0000")
 1230 !&B0008=fb% : !&B000C=bf% : !&B0010=np%*4
 1240 CALL &B0000
 1250 ENDPROC
 1260 :
 1270 REM ---- Toene -----------------------------------------------------
 1280 REM Direkt ueber die Audio-API des VDP (VDU 23,0,&85): Lautstaerke
 1290 REM vol% (0-127), Frequenz in Hz, Dauer in ms. Kanal 1 und 2 im
 1300 REM Wechsel: Der VDP verwirft Noten fuer einen noch belegten Kanal,
 1305 REM und TIME zaehlt nur in 20-ms-Schritten.
 1310 DEF PROCton(f%,ms%)
 1315 ch%=3-ch%
 1320 VDU 23,0,&85,ch%,0,vol%,f%;ms%;
 1330 PROCpause(ms% DIV 10+4)
 1340 ENDPROC
 1350 :
 1360 DEF PROCpause(cs%)
 1370 LOCAL t%
 1380 t%=TIME+cs%
 1390 REPEAT UNTIL TIME>=t%
 1400 ENDPROC
 1410 :
 1420 DEF PROCbereit
 1430 PRINT "Bereit - Taste: LED-Test, 2 Dauertest, 3 aus, 0 Ende"
 1440 PROCton(523,120) : PROCton(659,120) : PROCton(784,250)
 1450 ENDPROC
 1460 :
 1470 DEF PROCstart
 1480 PROCton(1047,60) : PROCton(1047,60)
 1490 ENDPROC
 1500 :
 1510 DEF PROCschritt(n%)
 1520 LOCAL j%
 1530 PROCpause(30)
 1540 FOR j%=1 TO n% : PROCton(1319,60) : PROCpause(10) : NEXT
 1550 PROCpause(30)
 1560 ENDPROC
 1570 :
 1580 DEF PROCklick
 1590 PROCton(1760,20)
 1600 ENDPROC
 1610 :
 1620 DEF PROCfertig
 1630 PROCton(784,120) : PROCton(659,120) : PROCton(523,300)
 1640 ENDPROC
 1650 :
 1660 DEF PROCende
 1670 PROCaus
 1680 PRINT "Ende - zurueck zu BASIC"
 1690 PROCfertig
 1700 ON ERROR OFF
 1710 END
 1720 :
 1730 REM ---- Fehler und ESC --------------------------------------------
 1740 REM ESC (Fehler 17) gilt als Abbruch, alles andere als Fehler.
 1750 DEF PROCfehler
 1760 LOCAL e%
 1770 e%=ERR
 1780 IF ok% THEN PROCaus
 1790 IF e%=17 THEN PRINT "Abgebrochen" : PROCfertig
 1800 IF e%<>17 THEN PRINT "Fehler ";e%;" in Zeile ";ERL;": "; : REPORT : PRINT : PROCton(196,300) : PROCpause(10) : PROCton(196,300) : PROCpause(10) : PROCton(196,300)
 1810 IF ok% THEN PROCbereit
 1820 ENDPROC
