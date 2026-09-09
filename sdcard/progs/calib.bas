   10 REM ================================================================
   20 REM  Kalibrierung der LED-Wand - Meilenstein M1
   30 REM
   40 REM  Ermittelt, welcher LED-Index auf welchem Pixel der 12x12-
   50 REM  Matrix sitzt, und legt das Ergebnis als matrix.map ab.
   60 REM
   70 REM  Verfahren: Es werden nacheinander drei einzelne LEDs
   80 REM  gezuendet. Zu jeder wird im Raster markiert, wo sie
   90 REM  aufleuchtet. Aus diesen drei Punkten waehlt das Programm
  100 REM  unter allen 16 moeglichen Verdrahtungen diejenige aus, die
  110 REM  passt. Bleiben mehrere uebrig, werden weitere LEDs gezeigt.
  120 REM
  130 REM  Fuer Sonderfaelle - etwa vertauschte Segmente - gibt es
  140 REM  zusaetzlich die vollstaendige Kalibrierung LED fuer LED.
  150 REM
  160 REM  Voraussetzung: ws2812.bin im selben Verzeichnis.
  170 REM ================================================================
  180 :
  190 PROCinit
  195 MODE 3 : *FX 4,1
  200 REPEAT
  210   PROCmenu
  220   m%=GET
  230   IF m%=49 THEN PROCquick
  240   IF m%=50 THEN PROCfull
  250   IF m%=51 THEN PROCverify
  260   IF m%=52 THEN PROCsave
  270   IF m%=53 THEN PROCload
  280   IF m%=54 THEN PROCshowmap
  290 UNTIL m%=48
  300 PROCalloff
  310 PRINT "Ende."
  320 END
  330 :
  340 REM ---- Menue ----------------------------------------------------
  350 DEF PROCmenu
  360 CLS
  370 PRINT "Kalibrierung der LED-Wand (M1)"
  380 PRINT "=============================="
  390 PRINT
  400 PRINT "  1  Schnellkalibrierung (drei LEDs)"
  410 PRINT "  2  Vollstaendig, LED fuer LED"
  420 PRINT "  3  Ergebnis pruefen"
  430 PRINT
  440 PRINT "  4  matrix.map speichern"
  450 PRINT "  5  matrix.map laden"
  460 PRINT "  6  Tabelle anzeigen"
  470 PRINT "  0  Beenden"
  480 PRINT
  490 PRINT "Stand: ";st$
  500 IF gp%=0 THEN PRINT "ACHTUNG: ws2812.bin fehlt - keine LED leuchtet."
  510 PRINT
  520 PRINT "Auswahl? ";
  530 ENDPROC
  540 :
  550 REM ---- Schnellkalibrierung --------------------------------------
  560 REM Drei Stuetzstellen genuegen fast immer: LED 0 legt die
  570 REM Startecke fest, LED 1 die Laufrichtung, LED wd% entscheidet
  580 REM zwischen Serpentine und progressiver Verdrahtung sowie
  590 REM zwischen zeilen- und spaltenweiser Fuehrung.
  600 DEF PROCquick
  610 LOCAL n%,k%,i%,c%
  620 PROCcands
  630 pr%(0)=0 : pr%(1)=1 : pr%(2)=wd% : pr%(3)=wd%+1 : pr%(4)=2*wd%
  640 n%=0
  650 REPEAT
  660   i%=pr%(n%)
  670   PROClight(i%)
  680   PROCpick("LED "+STR$(i%)+" leuchtet - Position markieren")
  690   IF cx%<0 THEN PROCalloff : ENDPROC
  700   PROCfilter(i%,cx%,cy%)
  710   n%=n%+1
  720   c%=FNcandcount
  730 UNTIL c%<=1 OR n%>4
  740 PROCalloff
  750 CLS
  760 IF c%=0 THEN PRINT "Keine bekannte Verdrahtung passt zu den" : PRINT "Eingaben. Bitte vollstaendig kalibrieren." : PRINT : PRINT "Taste"; : k%=GET : ENDPROC
  770 IF c%>1 THEN PRINT "Mehrere Verdrahtungen passen noch." : PRINT "Die erste davon wird uebernommen." : PRINT
  780 FOR k%=0 TO 15
  790   IF cd%(k%) THEN PROCbuild(k%) : k%=15
  800 NEXT
  810 PRINT "Uebernommen: ";st$
  820 PRINT
  830 PRINT "Mit Menuepunkt 3 pruefen, dann speichern."
  840 PRINT
  850 PRINT "Taste";
  860 k%=GET
  870 ENDPROC
  880 :
  890 REM ---- Vollstaendige Kalibrierung -------------------------------
  900 REM Jede LED einzeln. Mit ESC laesst sich jederzeit abbrechen;
  910 REM bereits markierte LEDs bleiben dann erhalten.
  920 DEF PROCfull
  930 LOCAL i%,k%
  940 FOR i%=0 TO np%-1
  950   PROClight(i%)
  960   PROCpick("LED "+STR$(i%)+" von "+STR$(np%-1)+" - Position markieren")
  970   IF cx%<0 THEN i%=np%-1 : GOTO 990
  980   mp%(cx%,cy%)=i%
  990 NEXT
 1000 PROCalloff
 1010 st$="vollstaendig kalibriert"
 1020 ENDPROC
 1030 :
 1040 REM ---- Pruefen ---------------------------------------------------
 1050 REM Laeuft die Kette ab und zeigt gleichzeitig im Raster, wo der
 1060 REM Punkt erscheinen muesste. Stimmen Anzeige und Wand ueberein,
 1070 REM ist die Tabelle richtig.
 1080 DEF PROCverify
 1090 LOCAL i%,x%,y%,k%
 1100 CLS
 1110 PRINT "Pruefung - Anzeige und Wand muessen uebereinstimmen."
 1120 PRINT "Taste haelt an, ESC bricht ab."
 1130 PROCgrid
 1140 FOR i%=0 TO np%-1
 1150   PROCfind(i%)
 1160   IF fx%<0 THEN GOTO 1220
 1170   PROCmark(fx%,fy%,"()")
 1180   PROClight(i%)
 1190   PRINT TAB(0,22);"LED-Index ";i%;"  Position ";fx%;",";fy%;"   ";
 1200   k%=INKEY(30)
 1210   PROCmark(fx%,fy%,". ")
 1220   IF k%=27 THEN i%=np%-1
 1230 NEXT
 1240 PROCalloff
 1250 PRINT TAB(0,23);"Fertig. Taste";
 1260 k%=GET
 1270 ENDPROC
 1280 :
 1290 REM ---- Raster mit Cursor ----------------------------------------
 1300 REM Liefert die gewaehlte Position in cx%,cy%. Bei ESC ist
 1310 REM cx% negativ. Pfeiltasten oder W/A/S/D, ENTER bestaetigt.
 1320 DEF PROCpick(t$)
 1330 LOCAL k%,ox%,oy%
 1340 CLS
 1350 PRINT t$
 1360 PRINT "Pfeiltasten oder WASD, ENTER bestaetigt, ESC bricht ab."
 1370 PROCgrid
 1380 cx%=0 : cy%=0
 1390 PROCmark(cx%,cy%,"[]")
 1400 REPEAT
 1410   PRINT TAB(0,22);"Position ";cx%;",";cy%;"    ";
 1420   k%=GET
 1430   ox%=cx% : oy%=cy%
 1440   IF k%=136 OR k%=97 OR k%=65 THEN cx%=cx%-1
 1450   IF k%=137 OR k%=100 OR k%=68 THEN cx%=cx%+1
 1460   IF k%=138 OR k%=115 OR k%=83 THEN cy%=cy%+1
 1470   IF k%=139 OR k%=119 OR k%=87 THEN cy%=cy%-1
 1480   IF cx%<0 THEN cx%=0
 1490   IF cx%>=wd% THEN cx%=wd%-1
 1500   IF cy%<0 THEN cy%=0
 1510   IF cy%>=ht% THEN cy%=ht%-1
 1520   IF cx%<>ox% OR cy%<>oy% THEN PROCmark(ox%,oy%,". ") : PROCmark(cx%,cy%,"[]")
 1530 UNTIL k%=13 OR k%=27
 1540 IF k%=27 THEN cx%=-1
 1550 ENDPROC
 1560 :
 1570 DEF PROCgrid
 1580 LOCAL x%,y%
 1590 PRINT TAB(0,4);"    ";
 1600 FOR x%=0 TO wd%-1
 1610   PRINT RIGHT$("  "+STR$(x%),2);" ";
 1620 NEXT
 1630 FOR y%=0 TO ht%-1
 1640   PRINT TAB(0,5+y%);RIGHT$("  "+STR$(y%),2);"  ";
 1650   FOR x%=0 TO wd%-1
 1660     PRINT ". ";
 1670   NEXT
 1680 NEXT
 1690 ENDPROC
 1700 :
 1710 DEF PROCmark(x%,y%,s$)
 1720 PRINT TAB(4+x%*3,5+y%);s$;
 1730 ENDPROC
 1740 :
 1750 REM ---- Kandidatenverfahren ---------------------------------------
 1760 REM 16 Varianten: zeilen- oder spaltenweise, Serpentine ja/nein,
 1770 REM und vier Startecken durch Spiegelung in x und y.
 1780 DEF PROCcands
 1790 LOCAL k%
 1800 FOR k%=0 TO 15
 1810   cd%(k%)=TRUE
 1820 NEXT
 1830 ENDPROC
 1840 :
 1850 REM Scheidet alle Varianten aus, bei denen LED i% nicht auf der
 1860 REM angegebenen Position sitzt.
 1870 DEF PROCfilter(i%,x%,y%)
 1880 LOCAL k%
 1890 FOR k%=0 TO 15
 1900   IF cd%(k%) AND FNidx(x%,y%,k%)<>i% THEN cd%(k%)=FALSE
 1910 NEXT
 1920 ENDPROC
 1930 :
 1940 DEF FNcandcount
 1950 LOCAL k%,n%
 1960 n%=0
 1970 FOR k%=0 TO 15
 1980   IF cd%(k%) THEN n%=n%+1
 1990 NEXT
 2000 =n%
 2010 :
 2020 REM Bit 0 = Serpentine, Bit 1 = spaltenweise,
 2030 REM Bit 2 = in x gespiegelt, Bit 3 = in y gespiegelt.
 2040 DEF FNidx(x%,y%,k%)
 2050 LOCAL a%,b%,t%,ln%
 2060 a%=x% : b%=y%
 2070 IF (k% AND 4) THEN a%=wd%-1-a%
 2080 IF (k% AND 8) THEN b%=ht%-1-b%
 2090 IF (k% AND 2) THEN t%=a% : a%=b% : b%=t%
 2100 ln%=wd%
 2110 IF (k% AND 2) THEN ln%=ht%
 2120 IF (k% AND 1) AND (b% AND 1)=1 THEN a%=ln%-1-a%
 2130 =b%*ln%+a%
 2140 :
 2150 DEF PROCbuild(k%)
 2160 LOCAL x%,y%
 2170 FOR y%=0 TO ht%-1
 2180   FOR x%=0 TO wd%-1
 2190     mp%(x%,y%)=FNidx(x%,y%,k%)
 2200   NEXT
 2210 NEXT
 2220 st$=FNcandname(k%)
 2230 ENDPROC
 2240 :
 2250 DEF FNcandname(k%)
 2260 LOCAL s$
 2270 s$="Variante "+STR$(k%)+": "
 2280 IF (k% AND 2) THEN s$=s$+"spaltenweise" ELSE s$=s$+"zeilenweise"
 2290 IF (k% AND 1) THEN s$=s$+", Serpentine" ELSE s$=s$+", progressiv"
 2300 IF (k% AND 4) THEN s$=s$+", x gespiegelt"
 2310 IF (k% AND 8) THEN s$=s$+", y gespiegelt"
 2320 =s$
 2330 :
 2340 REM Sucht die Position, an der LED i% sitzt.
 2350 DEF PROCfind(i%)
 2360 LOCAL x%,y%
 2370 fx%=-1 : fy%=-1
 2380 FOR y%=0 TO ht%-1
 2390   FOR x%=0 TO wd%-1
 2400     IF mp%(x%,y%)=i% THEN fx%=x% : fy%=y%
 2410   NEXT
 2420 NEXT
 2430 ENDPROC
 2440 :
 2450 REM ---- Tabelle anzeigen ------------------------------------------
 2460 DEF PROCshowmap
 2470 LOCAL x%,y%,k%,e%,i%
 2480 CLS
 2490 PRINT "Zuordnung Position -> LED-Index"
 2500 PRINT
 2510 FOR y%=0 TO ht%-1
 2520   FOR x%=0 TO wd%-1
 2530     PRINT RIGHT$("   "+STR$(mp%(x%,y%)),4);
 2540   NEXT
 2550   PRINT
 2560 NEXT
 2570 PRINT
 2580 REM Pruefen, ob jeder Index genau einmal vorkommt.
 2590 FOR i%=0 TO np%-1
 2600   sk%(i%)=0
 2610 NEXT
 2620 e%=0
 2630 FOR y%=0 TO ht%-1
 2640   FOR x%=0 TO wd%-1
 2650     i%=mp%(x%,y%)
 2660     IF i%>=0 AND i%<np% THEN sk%(i%)=sk%(i%)+1 ELSE e%=e%+1
 2670   NEXT
 2680 NEXT
 2690 FOR i%=0 TO np%-1
 2700   IF sk%(i%)<>1 THEN e%=e%+1
 2710 NEXT
 2720 IF e%=0 THEN PRINT "Vollstaendig: jeder Index genau einmal." ELSE PRINT "UNVOLLSTAENDIG: ";e%;" Abweichungen."
 2730 PRINT
 2740 PRINT "Taste";
 2750 k%=GET
 2760 ENDPROC
 2770 :
 2780 REM ---- Datei -----------------------------------------------------
 2790 REM Format: Byte 0 Breite, Byte 1 Hoehe, danach je Position ein
 2800 REM Byte mit dem LED-Index, zeilenweise von oben links.
 2810 DEF PROCsave
 2820 LOCAL f%,x%,y%,k%
 2830 CLS
 2840 f%=OPENOUT("matrix.map")
 2850 IF f%=0 THEN PRINT "Datei laesst sich nicht anlegen." : PRINT : PRINT "Taste"; : k%=GET : ENDPROC
 2860 BPUT#f%,wd%
 2870 BPUT#f%,ht%
 2880 FOR y%=0 TO ht%-1
 2890   FOR x%=0 TO wd%-1
 2900     BPUT#f%,mp%(x%,y%)
 2910   NEXT
 2920 NEXT
 2930 CLOSE#f%
 2940 PRINT "matrix.map geschrieben (";np%+2;" Byte)."
 2950 PRINT
 2960 PRINT "Taste";
 2970 k%=GET
 2980 ENDPROC
 2990 :
 3000 DEF PROCload
 3010 LOCAL f%,x%,y%,k%,w%,h%
 3020 CLS
 3030 f%=OPENIN("matrix.map")
 3040 IF f%=0 THEN PRINT "matrix.map nicht gefunden." : PRINT : PRINT "Taste"; : k%=GET : ENDPROC
 3050 w%=BGET#f%
 3060 h%=BGET#f%
 3070 IF w%<>wd% OR h%<>ht% THEN CLOSE#f% : PRINT "Passt nicht: Datei ist ";w%;"x";h%;"." : PRINT : PRINT "Taste"; : k%=GET : ENDPROC
 3080 FOR y%=0 TO ht%-1
 3090   FOR x%=0 TO wd%-1
 3100     mp%(x%,y%)=BGET#f%
 3110   NEXT
 3120 NEXT
 3130 CLOSE#f%
 3140 st$="aus matrix.map geladen"
 3150 PRINT "matrix.map geladen."
 3160 PRINT
 3170 PRINT "Taste";
 3180 k%=GET
 3190 ENDPROC
 3200 :
 3210 REM ---- LED-Ansteuerung -------------------------------------------
 3220 REM Bewusst dunkel: bei der Kalibrierung zaehlt nur, welche LED
 3230 REM leuchtet, nicht wie hell.
 3240 DEF PROClight(i%)
 3250 LOCAL j%
 3260 IF gp%=0 THEN ENDPROC
 3270 FOR j%=0 TO np%-1
 3280   !(fb%+j%*4)=0
 3290 NEXT
 3300 ?(fb%+i%*4+0)=30
 3310 ?(fb%+i%*4+1)=30
 3320 ?(fb%+i%*4+2)=30
 3330 PROCsend
 3340 ENDPROC
 3350 :
 3360 DEF PROCalloff
 3370 LOCAL j%
 3380 IF gp%=0 THEN ENDPROC
 3390 FOR j%=0 TO np%-1
 3400   !(fb%+j%*4)=0
 3410 NEXT
 3420 PROCsend
 3430 ENDPROC
 3440 :
 3450 DEF PROCsend
 3460 IF ?&B0000<>&C3 THEN OSCLI("LOAD ws2812.bin &B0000")
 3470 !&B0008=fb%
 3480 !&B000C=bf%
 3490 !&B0010=np%*4
 3500 CALL &B0000
 3510 ENDPROC
 3520 :
 3530 REM ---- Initialisierung -------------------------------------------
 3540 DEF PROCinit
 3550 wd%=12 : ht%=12 : np%=wd%*ht%
 3560 DIM mp%(wd%-1,ht%-1)
 3570 DIM cd%(15)
 3580 DIM pr%(4)
 3590 DIM sk%(np%-1)
 3595 DIM rf%(wd%-1,ht%-1)
 3600 DIM fb% np%*4-1
 3610 DIM bf% np%*32-1
 3620 st$="noch nicht kalibriert"
 3630 REM Startbelegung: Serpentine zeilenweise ab oben links.
 3640 PROCbuild(1)
 3650 st$="Vorgabe, noch nicht kalibriert"
 3680 gp%=0
 3690 OSCLI("LOAD ws2812.bin &B0000")
 3700 IF ?&B0000=&C3 THEN CALL &B0004 : gp%=TRUE
 3710 ENDPROC
 3720 :
 3730 REM ================================================================
 3740 REM  Selbsttest - prueft das Kandidatenverfahren ohne Hardware
 3750 REM  und ohne Bildschirmmodus, laeuft daher im CLI-Emulator:
 3760 REM     LOAD "calib.bas" : PROCinit : PROCselftest
 3770 REM ================================================================
 3780 DEF PROCselftest
 3790 LOCAL k%,n%,i%,x%,y%,c%,q%,bad%,amb%
 3800 PRINT "Selbsttest Kandidatenverfahren"
 3810 PRINT "=============================="
 3820 PRINT
 3830 PRINT "Fuer jede der 16 Verdrahtungen wird geprueft, ob sie sich"
 3840 PRINT "aus den Stuetzstellen wiederfinden laesst."
 3850 PRINT
 3860 pr%(0)=0 : pr%(1)=1 : pr%(2)=wd% : pr%(3)=wd%+1 : pr%(4)=2*wd%
 3870 bad%=0 : amb%=0
 3880 FOR k%=0 TO 15
 3890   PROCbuild(k%)
 3900   FOR y%=0 TO ht%-1
 3910     FOR x%=0 TO wd%-1
 3920       rf%(x%,y%)=mp%(x%,y%)
 3930     NEXT
 3940   NEXT
 3950   PROCcands
 3960   FOR n%=0 TO 4
 3970     i%=pr%(n%)
 3980     PROCfind(i%)
 3990     PROCfilter(i%,fx%,fy%)
 4000   NEXT
 4010   c%=FNcandcount
 4020   q%=FNmatches(k%)
 4030   IF c%=0 OR q%=0 THEN bad%=bad%+1
 4040   IF c%>1 THEN amb%=amb%+1
 4050   PRINT "  ";RIGHT$("  "+STR$(k%),2);"  Kandidaten ";c%;
 4060   IF q%>0 AND c%>0 THEN PRINT "  identisch: ";q%;"  OK" ELSE PRINT "  FEHLER"
 4070 NEXT
 4080 PRINT
 4090 IF bad%=0 THEN PRINT "Alle 16 Verdrahtungen wiedergefunden." ELSE PRINT bad%;" nicht wiedergefunden!"
 4100 PRINT amb%;" Faelle mit mehr als einem Kandidaten."
 4110 PRINT "Mehrdeutig heisst hier: die Kandidaten erzeugen dieselbe"
 4120 PRINT "Zuordnung, sind also gleichwertig."
 4130 PRINT
 4140 PROCbuild(1)
 4150 ENDPROC
 4160 :
 4170 REM Zaehlt, wie viele verbliebene Kandidaten dieselbe Zuordnung
 4180 REM erzeugen wie das gesicherte Referenz-Mapping.
 4190 DEF FNmatches(k0%)
 4200 LOCAL k%,x%,y%,n%,ok%
 4210 n%=0
 4220 FOR k%=0 TO 15
 4230   IF cd%(k%)=FALSE THEN GOTO 4290
 4240   ok%=TRUE
 4250   FOR y%=0 TO ht%-1
 4260     FOR x%=0 TO wd%-1
 4270       IF FNidx(x%,y%,k%)<>rf%(x%,y%) THEN ok%=FALSE
 4280   NEXT : NEXT
 4290   IF cd%(k%) AND ok% THEN n%=n%+1
 4300 NEXT
 4310 =n%
