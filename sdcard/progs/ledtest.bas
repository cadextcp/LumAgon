   10 REM ================================================================
   20 REM  Erstinbetriebnahme der LED-Wand
   30 REM
   40 REM  Minimalprogramm ohne Grafik und Menue: nur Textausgabe und
   50 REM  einzelne LEDs. Gedacht fuer den ersten Kontakt mit echter
   60 REM  Hardware, wenn noch unklar ist, ob Verkabelung und Timing
   70 REM  stimmen. Absichtlich sehr dunkel, damit der Strom klein
   80 REM  bleibt und ein Verdrahtungsfehler nichts beschaedigt.
   90 REM
   92 REM  Lumanode: 2 LEDs je Pixel. ws2812.asm sendet jeden der 144
   94 REM  Eintraege zweimal (288 LEDs) und begrenzt jeden Kanal auf
   96 REM  hoechstens 90 von 255 - 60 im Programm sind am Draht ~20.
  100 REM  Voraussetzung: ws2812.bin liegt im selben Verzeichnis.
  110 REM    /bin/ez80asm ws2812.asm ws2812.bin -oB0000 -a1
  120 REM ================================================================
  130 :
  140 nl%=144 : REM Pixel = Framebuffer-Eintraege
  150 DIM fb% nl%*4-1
  160 DIM bf% nl%*64-1 : REM 8 Byte je fb-Byte, 2 LEDs je Pixel
  170 :
  180 PRINT "LED-Wand Inbetriebnahme"
  190 PRINT "======================="
  200 PRINT
  210 PRINT "Datenleitung: PC4 = Pin 21"
  220 PRINT "Masse       : Pin 3, 5 oder 33"
  230 PRINT
  240 OSCLI("LOAD ws2812.bin &B0000")
  250 IF ?&B0000<>&C3 THEN PRINT "ws2812.bin nicht geladen!" : END
  260 CALL &B0004
  270 PRINT "Routine geladen, PC4 ist Ausgang."
  280 PRINT
  290 :
  300 REM ---- Test 1: nur die erste LED, ein Kanal nach dem anderen ----
  310 PRINT "Test 1 - Pixel 0 (LED 0 und 1) einzeln"
  320 PROCone(0,60,0,0,0,"rot")
  330 PROCone(0,0,60,0,0,"gruen")
  340 PROCone(0,0,0,60,0,"blau")
  350 PROCone(0,0,0,0,60,"weiss (W-Kanal)")
  360 PRINT
  370 :
  380 REM ---- Test 2: die ersten zwoelf LEDs, zeigt die Kettenrichtung -
  390 PRINT "Test 2 - Pixel 0 bis 11 in Kettenfolge"
  400 FOR i%=0 TO 11
  410   PROCclear
  420   PROCset(i%,45,45,45,0)
  430   PROCsend
  440   PRINT "  Pixel ";i%;" = LED ";i%*2;"+";i%*2+1;" - Taste";
  450   t%=GET
  460   PRINT
  470 NEXT
  480 PRINT
  490 :
  500 REM ---- Test 3: alle LEDs sehr dunkel ---------------------------
  510 PRINT "Test 3 - alle ";nl%*2;" LEDs schwach weiss"
  520 PRINT "Bei falschem Timing sind die Farben bunt statt weiss."
  530 PROCclear
  540 FOR i%=0 TO nl%-1
  550   PROCset(i%,24,24,24,0)
  560 NEXT
  570 PROCsend
  580 PRINT "Taste zum Ausschalten";
  590 t%=GET
  600 PRINT
  610 PROCclear
  620 PROCsend
  630 PRINT "Fertig - alles aus."
  640 END
  650 :
  660 REM ---- Hilfsroutinen -------------------------------------------
  670 DEF PROCone(i%,r%,g%,b%,w%,n$)
  680 PROCclear
  690 PROCset(i%,r%,g%,b%,w%)
  700 PROCsend
  710 PRINT "  ";n$;" - Taste";
  720 t%=GET
  730 PRINT
  740 ENDPROC
  750 :
  760 REM Framebuffer in der Reihenfolge G,R,B,W
  770 DEF PROCset(i%,r%,g%,b%,w%)
  780 LOCAL o%
  790 IF i%<0 OR i%>=nl% THEN ENDPROC
  800 o%=fb%+i%*4
  810 ?(o%+0)=g% : ?(o%+1)=r%
  820 ?(o%+2)=b% : ?(o%+3)=w%
  830 ENDPROC
  840 :
  850 DEF PROCclear
  860 LOCAL i%
  870 FOR i%=0 TO nl%-1
  880   !(fb%+i%*4)=0
  890 NEXT
  900 ENDPROC
  910 :
  920 DEF PROCsend
  930 IF ?&B0000<>&C3 THEN OSCLI("LOAD ws2812.bin &B0000")
  940 !&B0008=fb%
  950 !&B000C=bf%
  960 !&B0010=nl%*4
  970 CALL &B0000
  980 ENDPROC
