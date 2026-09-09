   10 REM ================================================================
   20 REM  LED-Wand 12x12 - Meilenstein M0
   30 REM  Framebuffer, Mapping und Bildschirm-Vorschau
   40 REM
   50 REM  Laeuft vollstaendig im Emulator, ohne angeschlossene Hardware.
   60 REM  Siehe docs/PLAN.md
   70 REM ================================================================
   80 :
   90 REM ---- Hauptprogramm --------------------------------------------
  100 PROCinit
  110 REPEAT
  120   PROCmenu
  130     m%=GET
  140     IF m%=49 THEN PROCdemochain
  150     IF m%=50 THEN PROCdemoorient
  160     IF m%=51 THEN PROCdemochannels
  170     IF m%=52 THEN PROCdemorainbow
  180     IF m%=53 THEN PROCsetstyle
  190     IF m%=54 THEN PROCsetbright
  195     IF m%=55 THEN PROCselftest
  196     IF m%=56 THEN PROCsetbackend
  200 UNTIL m%=48
  210 MODE 3
  220 PRINT "Ende."
  230 END
  240 :
  250 REM ---- Menue ----------------------------------------------------
  260 DEF PROCmenu
  270 MODE 3
  280 PRINT "LED-Wand 12x12 - Vorschau (M0)"
  290 PRINT "=============================="
  300 PRINT
  310 PRINT "  1  Kettenlauf (zeigt Verdrahtung)"
  320 PRINT "  2  Orientierungstest (Ecken/Achsen)"
  330 PRINT "  3  Kanaltest R/G/B/W"
  340 PRINT "  4  Regenbogen (animiert)"
  350 PRINT
  360 PRINT "  5  Mapping umschalten"
  370 PRINT "  6  Helligkeit einstellen"
  375 PRINT "  7  Selbsttest (nur Text)"
  376 PRINT "  8  Ausgabe: Vorschau / LED-Wand"
  380 PRINT "  0  Beenden"
  390 PRINT
  400 PRINT "Mapping   : ";FNstylename(style%)
  410 PRINT "Helligkeit: ";bri%;" von 255"
  415 PRINT "Ausgabe   : ";FNbkname(bk%)
  420 PRINT
  430 PRINT "Auswahl? ";
  440 ENDPROC
  450 :
  460 REM ---- Demo 1: Kettenlauf ---------------------------------------
  470 REM Laeuft die LED-Kette in Reihenfolge des Datensignals ab.
  480 REM Damit sieht man sofort, wie der Streifen verlegt ist.
  490 DEF PROCdemochain
  500 PROCscreen
  510 PROCcls
  520 FOR i%=0 TO 143
  530   IF i%>0 THEN PROCpixi(i%-1,0,40,0,0)
  540   IF i%>6 THEN PROCpixi(i%-7,0,0,0,0)
  550   PROCpixi(i%,255,255,255,0)
  560   PROCshow
  570   PROCstatus("LED-Index "+STR$(i%))
  580   IF INKEY(0)>=0 THEN i%=143
  590 NEXT
  600 PROCwait
  610 ENDPROC
  620 :
  630 REM ---- Demo 2: Orientierung -------------------------------------
  640 REM Markiert die vier Ecken und die beiden Achsen, damit die
  650 REM Ausrichtung der Matrix eindeutig bestimmbar ist.
  660 DEF PROCdemoorient
  670 PROCscreen
  680 PROCcls
  690 FOR x%=1 TO 11
  700   PROCpix(x%,0,80,0,0,0)
  710 NEXT
  720 FOR y%=1 TO 11
  730   PROCpix(0,y%,0,0,80,0)
  740 NEXT
  750 PROCpix(0,0,255,255,255,0)
  760 PROCpix(11,0,255,0,0,0)
  770 PROCpix(0,11,0,0,255,0)
  780 PROCpix(11,11,0,255,0,0)
  790 PROCshow
  800 PROCstatus("weiss=0,0  rot=11,0  blau=0,11  gruen=11,11")
  810 PROCwait
  820 ENDPROC
  830 :
  840 REM ---- Demo 3: Kanaltest ----------------------------------------
  850 DEF PROCdemochannels
  860 PROCscreen
  870 FOR k%=0 TO 3
  880   FOR y%=0 TO 11
  890     FOR x%=0 TO 11
  900       r%=0 : g%=0 : b%=0 : w%=0
  910       IF k%=0 THEN r%=255
  920       IF k%=1 THEN g%=255
  930       IF k%=2 THEN b%=255
  940       IF k%=3 THEN w%=255
  950       PROCpix(x%,y%,r%,g%,b%,w%)
  960     NEXT
  970   NEXT
  980   PROCshow
  990   PROCstatus("Kanal "+MID$("RGBW",k%+1,1)+" - Taste fuer weiter")
 1000   t%=GET
 1010 NEXT
 1020 ENDPROC
 1030 :
 1040 REM ---- Demo 4: Regenbogen ---------------------------------------
 1050 REM Nutzt die Sinustabelle statt SIN(), sonst waere es zu langsam.
 1060 DEF PROCdemorainbow
 1070 PROCscreen
 1080 f%=0 : t0%=TIME
 1090 REPEAT
 1100   FOR y%=0 TO 11
 1110     FOR x%=0 TO 11
 1120       p%=(f%+(x%+y%)*3) AND 63
 1130       PROCpix(x%,y%,sn%(p%),sn%((p%+21) AND 63),sn%((p%+42) AND 63),0)
 1140     NEXT
 1150   NEXT
 1160   PROCshow
 1170   f%=f%+1
 1180 UNTIL INKEY(0)>=0
 1190 e%=TIME-t0%
 1200 IF e%<1 THEN e%=1
 1210 PROCstatus("Frames "+STR$(f%)+"  fps "+STR$((f%*100) DIV e%))
 1220 PROCwait
 1230 ENDPROC
 1240 :
 1250 REM ---- Einstellungen --------------------------------------------
 1260 DEF PROCsetstyle
 1270 MODE 3
 1280 PRINT "Verdrahtung der Matrix"
 1290 PRINT "======================"
 1300 PRINT
 1310 PRINT "  0  Serpentine zeilenweise (Standard)"
 1320 PRINT "  1  Progressiv zeilenweise"
 1330 PRINT "  2  Serpentine spaltenweise"
 1332 PRINT "  3  aus matrix.map (von calib.bas erzeugt)"
 1340 PRINT
 1350 PRINT "Auswahl? ";
 1360 s%=GET-48
 1370 IF s%>=0 AND s%<=2 THEN style%=s% : PROCmapbuild(style%)
 1372 IF s%=3 THEN PROCloadmap : IF NOT mapok% THEN PRINT : PRINT "matrix.map nicht gefunden oder passt nicht." : t%=GET
 1375 PROCinvalidate
 1380 ENDPROC
 1390 :
 1400 DEF PROCsetbright
 1410 MODE 3
 1420 PRINT "Helligkeit 0-255, aktuell ";bri%
 1430 PRINT
 1440 INPUT "Neuer Wert: " v%
 1450 IF v%<0 THEN v%=0
 1460 IF v%>255 THEN v%=255
 1470 bri%=v%
 1473 PROCbuildcol
 1476 PROCinvalidate
 1480 ENDPROC
 1490 :
 1500 REM ================================================================
 1510 REM  Bibliothek - unveraendert in andere Programme uebernehmen
 1520 REM ================================================================
 1530 :
 1540 REM ---- Initialisierung ------------------------------------------
 1550 DEF PROCinit
 1560 LOCAL i%
 1570 wd%=12 : ht%=12 : np%=wd%*ht%
 1580 DIM fb% np%*4-1
 1590 DIM mp%(wd%-1,ht%-1)
 1595 DIM sk%(np%-1)
 1596 DIM pv%(np%-1)
 1597 DIM cr%(255) : DIM cg%(255) : DIM cb%(255)
 1598 DIM bf% np%*32-1
 1600 DIM sn%(63)
 1610 FOR i%=0 TO 63
 1620   sn%(i%)=128+127*SIN(i%*2*PI/64)
 1630 NEXT
 1640 bri%=255
 1645 PROCbuildcol
 1646 bk%=0 : gpok%=FALSE
 1650 style%=0
 1660 PROCmapbuild(style%)
 1665 REM Liegt eine Kalibrierung vor, hat sie Vorrang.
 1667 PROCloadmap
 1670 REM Layout der Vorschau in logischen Koordinaten (1280x1024).
 1680 REM 80x85 pro Zelle ergibt physisch quadratische 20x20 Pixel.
 1690 gx%=160 : gy%=937 : cw%=80 : ch%=85
 1700 PROCcls
 1705 PROCinvalidate
 1710 ENDPROC
 1720 :
 1730 REM ---- Mapping: Pixelkoordinate -> LED-Index --------------------
 1740 REM Tabelle statt Formel, damit spaeter auch eine per Kalibrierung
 1750 REM ermittelte oder fehlerhafte Verdrahtung abbildbar ist (M1).
 1760 DEF PROCmapbuild(st%)
 1762 REM Stil 3 ist keine Formel, sondern die kalibrierte Tabelle.
 1764 REM Ohne diese Weiche wuerde die Schleife unten sie mit Nullen
 1766 REM ueberschreiben, sobald jemand PROCmapbuild(style%) aufruft.
 1768 IF st%=3 THEN PROCloadmap : ENDPROC
 1770 LOCAL x%,y%,i%
 1780 FOR y%=0 TO ht%-1
 1790   FOR x%=0 TO wd%-1
 1800     i%=0
 1810     IF st%=0 AND (y% AND 1)=0 THEN i%=y%*wd%+x%
 1820     IF st%=0 AND (y% AND 1)=1 THEN i%=y%*wd%+wd%-1-x%
 1830     IF st%=1 THEN i%=y%*wd%+x%
 1840     IF st%=2 AND (x% AND 1)=0 THEN i%=x%*ht%+y%
 1850     IF st%=2 AND (x% AND 1)=1 THEN i%=x%*ht%+ht%-1-y%
 1860     mp%(x%,y%)=i%
 1870   NEXT
 1880 NEXT
 1890 ENDPROC
 1900 :
 1910 DEF FNstylename(s%)
 1920 IF s%=0 THEN ="Serpentine zeilenweise"
 1930 IF s%=1 THEN ="Progressiv zeilenweise"
 1935 IF s%=3 THEN ="aus matrix.map (kalibriert)"
 1940 ="Serpentine spaltenweise"
 1950 :
 1960 REM ---- Framebuffer ----------------------------------------------
 1970 REM 4 Byte je LED in der Reihenfolge G,R,B,W - genau so, wie die
 1980 REM Bytes spaeter auf den Draht gehen. Die Ausgaberoutine in M2
 1990 REM schiebt den Puffer dadurch nur noch linear hinaus.
 2000 DEF PROCpix(x%,y%,r%,g%,b%,w%)
 2010 IF x%<0 OR x%>=wd% OR y%<0 OR y%>=ht% THEN ENDPROC
 2020 PROCpixi(mp%(x%,y%),r%,g%,b%,w%)
 2030 ENDPROC
 2040 :
 2050 DEF PROCpixi(i%,r%,g%,b%,w%)
 2052 REM Begrenzung inline statt per FN: Funktionsaufrufe sind in
 2054 REM BASIC teuer, und dies ist die meistgenutzte Routine.
 2056 LOCAL o%
 2058 IF i%<0 OR i%>=np% THEN ENDPROC
 2060 IF r%<0 THEN r%=0
 2062 IF r%>255 THEN r%=255
 2064 IF g%<0 THEN g%=0
 2066 IF g%>255 THEN g%=255
 2068 IF b%<0 THEN b%=0
 2070 IF b%>255 THEN b%=255
 2072 IF w%<0 THEN w%=0
 2074 IF w%>255 THEN w%=255
 2076 o%=fb%+i%*4
 2078 ?(o%+0)=g% : ?(o%+1)=r%
 2080 ?(o%+2)=b% : ?(o%+3)=w%
 2130 ENDPROC
 2190 :
 2200 DEF PROCcls
 2210 LOCAL i%
 2220 FOR i%=0 TO np%-1
 2230   !(fb%+i%*4)=0
 2240 NEXT
 2250 ENDPROC
 2260 :
 2270 REM ---- Renderer -------------------------------------------------
 2280 REM Einziger Ort, an dem der Framebuffer ausgegeben wird. In M2
 2290 REM kommt hier das GPIO-Backend daneben; alles darueber bleibt gleich.
 2300 DEF PROCshow
 2310 IF bk%<>1 THEN PROCrendervdp
 2315 IF bk%>0 THEN PROCsendgpio
 2320 ENDPROC
 2330 :
 2340 DEF PROCrendervdp
 2342 REM Es werden nur geaenderte Zellen neu gezeichnet. Die VDU-
 2344 REM Ausgabe ist der Flaschenhals, nicht die Rechnung.
 2350 LOCAL x%,y%,i%,c%,o%
 2360 FOR y%=0 TO ht%-1
 2370   FOR x%=0 TO wd%-1
 2380     i%=mp%(x%,y%) : o%=fb%+i%*4
 2390     c%=FNcol(?(o%+1),?(o%+0),?(o%+2),?(o%+3))
 2400     IF c%<>pv%(i%) THEN pv%(i%)=c% : PROCcell(x%,y%,c%)
 2440   NEXT
 2450 NEXT
 2460 ENDPROC
 2462 :
 2464 DEF PROCcell(x%,y%,c%)
 2465 LOCAL x1%,y1%
 2466 GCOL 0,c%
 2467 x1%=gx%+x%*cw%
 2468 y1%=gy%-y%*ch%
 2469 MOVE x1%+4,y1%+4
 2471 PLOT 101,x1%+cw%-8,y1%+ch%-8
 2472 ENDPROC
 2473 :
 2474 REM Nach einem Bildschirmwechsel ist der Cache ungueltig.
 2475 DEF PROCinvalidate
 2476 LOCAL i%
 2477 FOR i%=0 TO np%-1 : pv%(i%)=-1 : NEXT
 2478 ENDPROC
 2480 REM Physische Agon-Farben sind 6 Bit im Format RRGGBB.
 2490 REM Der Weisskanal wird fuer die Vorschau additiv eingerechnet,
 2500 REM die Helligkeit hier angewandt - nicht im Framebuffer.
 2510 DEF FNcol(r%,g%,b%,w%)
 2520 LOCAL p%,q%,s%
 2530 p%=r%+w% : IF p%>255 THEN p%=255
 2540 q%=g%+w% : IF q%>255 THEN q%=255
 2550 s%=b%+w% : IF s%>255 THEN s%=255
 2560 =cr%(p%)+cg%(q%)+cb%(s%)
 2570 :
 2580 REM ---- Bildschirm-Hilfen ----------------------------------------
 2590 DEF PROCscreen
 2600 MODE 8
 2605 PROCinvalidate
 2610 ENDPROC
 2620 :
 2630 DEF PROCstatus(s$)
 2640 PRINT TAB(0,28);s$;SPC(39-LEN(s$));
 2650 ENDPROC
 2660 :
 2670 DEF PROCwait
 2680 PRINT TAB(0,29);"Taste druecken";
 2690 t%=GET
 2700 ENDPROC
 2710 :
 2720 REM ================================================================
 2730 REM  Selbsttest - reine Textausgabe, laeuft auch im CLI-Emulator
 2740 REM ================================================================
 2750 DEF PROCselftest
 2760 LOCAL s%,x%,y%,i%,e%,o%
 2770 REM Kein MODE-Wechsel: so auch im CLI-Emulator aufrufbar mit
 2775 REM   LOAD "ledmatrix.bas" : PROCinit : PROCselftest
 2780 PRINT "Selbsttest"
 2790 PRINT "=========="
 2800 PRINT
 2810 PRINT "Mapping - jeder LED-Index genau einmal:"
 2820 FOR s%=0 TO 2
 2830   PROCmapbuild(s%)
 2840   e%=0
 2850   FOR i%=0 TO np%-1
 2860     sk%(i%)=0
 2870   NEXT
 2880   FOR y%=0 TO ht%-1
 2890     FOR x%=0 TO wd%-1
 2900       i%=mp%(x%,y%)
 2910       IF i%<0 OR i%>=np% THEN e%=e%+1
 2920       IF i%>=0 AND i%<np% THEN sk%(i%)=sk%(i%)+1
 2930     NEXT
 2940   NEXT
 2950   FOR i%=0 TO np%-1
 2960     IF sk%(i%)<>1 THEN e%=e%+1
 2970   NEXT
 2980   PRINT "  Stil ";s%;" ";FNstylename(s%);
 2990   IF e%=0 THEN PRINT " : OK" ELSE PRINT " : FEHLER ";e%
 3000 NEXT
 3010 PROCmapbuild(style%)
 3020 PRINT
 3030 PRINT "Tabelle fuer ";FNstylename(style%);":"
 3040 FOR y%=0 TO ht%-1
 3050   FOR x%=0 TO wd%-1
 3060     PRINT RIGHT$("   "+STR$(mp%(x%,y%)),4);
 3070   NEXT
 3080   PRINT
 3090 NEXT
 3100 PRINT
 3110 PRINT "Framebuffer (Reihenfolge G,R,B,W):"
 3120 PROCcls
 3130 PROCpix(3,5,10,20,30,40)
 3140 o%=fb%+mp%(3,5)*4
 3150 PRINT "  pix(3,5,r10,g20,b30,w40) -> ";?(o%+0);" ";?(o%+1);" ";?(o%+2);" ";?(o%+3);
 3160 IF ?(o%+0)=20 AND ?(o%+1)=10 AND ?(o%+2)=30 AND ?(o%+3)=40 THEN PRINT "  OK" ELSE PRINT "  FEHLER"
 3170 PROCpixi(0,300,-5,128,0)
 3180 PRINT "  Begrenzung 300/-5/128     -> ";?(fb%+1);" ";?(fb%+0);" ";?(fb%+2);
 3190 IF ?(fb%+1)=255 AND ?(fb%+0)=0 AND ?(fb%+2)=128 THEN PRINT "  OK" ELSE PRINT "  FEHLER"
 3200 PRINT
 3210 PRINT "Farbumrechnung (6 Bit RRGGBB), Helligkeit ";bri%;":"
 3220 PRINT "  rot 48 gruen 12 blau 3 weiss 63 -> ";
 3230 PRINT STR$(FNcol(255,0,0,0));" ";STR$(FNcol(0,255,0,0));" ";STR$(FNcol(0,0,255,0));" ";STR$(FNcol(0,0,0,255))
 3240 PRINT
 3250 PRINT "Taste druecken";
 3260 t%=GET
 3270 ENDPROC
 3280 :
 3290 REM ================================================================
 3300 REM  Farbtabellen (gehoert zur Bibliothek, steht hier nur wegen
 3310 REM  der Zeilennummern-Vergabe)
 3320 REM ================================================================
 3330 REM Die Tabellen enthalten Quantisierung auf 2 Bit je Kanal und
 3340 REM die Helligkeit. Das spart pro Pixel drei Multiplikationen und
 3350 REM drei Divisionen - in BASIC der teuerste Teil des Renderns.
 3360 REM Nach jeder Aenderung von bri% neu aufbauen.
 3370 DEF PROCbuildcol
 3380 LOCAL v%,q%
 3390 FOR v%=0 TO 255
 3400   q%=(v%*bri% DIV 255) DIV 64
 3410   cr%(v%)=q%*16 : cg%(v%)=q%*4 : cb%(v%)=q%
 3420 NEXT
 3430 ENDPROC
 3440 :
 3450 REM ================================================================
 3460 REM  GPIO-Backend (M2) - Ausgabe an die echte LED-Kette
 3470 REM ================================================================
 3480 REM Die zeitkritische Bitausgabe steckt in ws2812.bin, erzeugt aus
 3490 REM ws2812.asm. BASIC liefert nur den Framebuffer und die Adressen.
 3500 REM Ladeadresse &B0000 ist der MOS-Bereich fuer Star-Command-
 3510 REM Programme; ein dort gestartetes Moslet wuerde den Code
 3520 REM ueberschreiben, deshalb die Pruefung in PROCsendgpio.
 3530 DEF PROCgpioload
 3540 OSCLI("LOAD ws2812.bin &B0000")
 3550 CALL &B0004
 3560 gpok%=TRUE
 3570 ENDPROC
 3580 :
 3590 DEF PROCsendgpio
 3600 IF NOT gpok% THEN ENDPROC
 3610 IF ?&B0000<>&C3 THEN PROCgpioload
 3620 !&B0008=fb%
 3630 !&B000C=bf%
 3640 !&B0010=np%*4
 3650 CALL &B0000
 3660 ENDPROC
 3670 :
 3680 REM Umschalten zwischen Vorschau, echter Ausgabe und beidem.
 3690 REM Beim ersten Einschalten wird die Routine nachgeladen; fehlt
 3700 REM ws2812.bin, faellt das Programm auf reine Vorschau zurueck.
 3710 DEF PROCsetbackend
 3720 MODE 3
 3730 PRINT "Ausgabe"
 3740 PRINT "======="
 3750 PRINT
 3760 PRINT "  0  nur Bildschirm-Vorschau"
 3770 PRINT "  1  nur LED-Wand (GPIO, PC4 = Pin 21)"
 3780 PRINT "  2  beides"
 3790 PRINT
 3800 PRINT "Auswahl? ";
 3810 s%=GET-48
 3820 IF s%<0 OR s%>2 THEN ENDPROC
 3830 IF s%=0 THEN bk%=0 : ENDPROC
 3840 ON ERROR LOCAL PRINT "ws2812.bin fehlt - bleibe bei Vorschau" : gpok%=FALSE : bk%=0 : t%=GET : ENDPROC
 3850 IF NOT gpok% THEN PROCgpioload
 3860 bk%=s%
 3870 ENDPROC
 3880 :
 3890 DEF FNbkname(b%)
 3900 IF b%=0 THEN ="nur Vorschau"
 3910 IF b%=1 THEN ="nur LED-Wand"
 3920 ="Vorschau und LED-Wand"
 3930 :
 3940 REM ================================================================
 3950 REM  Kalibriertes Mapping laden (M1)
 3960 REM ================================================================
 3970 REM matrix.map wird von calib.bas geschrieben: Byte 0 Breite,
 3980 REM Byte 1 Hoehe, danach je Position ein Byte mit dem LED-Index.
 3990 REM Fehlt die Datei, bleibt das eingestellte Standard-Mapping.
 4000 DEF PROCloadmap
 4010 LOCAL f%,x%,y%,w%,h%
 4020 mapok%=FALSE
 4030 f%=OPENIN("matrix.map")
 4040 IF f%=0 THEN ENDPROC
 4050 w%=BGET#f%
 4060 h%=BGET#f%
 4070 IF w%<>wd% OR h%<>ht% THEN CLOSE#f% : ENDPROC
 4080 FOR y%=0 TO ht%-1
 4090   FOR x%=0 TO wd%-1
 4100     mp%(x%,y%)=BGET#f%
 4110   NEXT
 4120 NEXT
 4130 CLOSE#f%
 4140 mapok%=TRUE
 4150 style%=3
 4160 ENDPROC
