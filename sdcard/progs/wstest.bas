   10 REM ================================================================
   20 REM  Selbsttest fuer ws2812.bin - laeuft im Emulator
   30 REM
   40 REM  Prueft das Entpacken in den Bitpuffer: Verdopplung je Pixel,
   50 REM  Helligkeitsbremse, Bitreihenfolge, keine Pufferueberschreitung.
   60 REM  Das Timing prueft er nicht - das kann nur echte Hardware.
   70 REM  Die Ausgabe auf PC4 geht im Emulator ins Leere.
   80 REM
   90 REM    /bin/ez80asm ws2812.asm ws2812.bin -oB0000 -a1
  100 REM    LOAD "wstest.bas" : RUN
  110 REM ================================================================
  120 :
  130 ne%=144
  140 DIM fb% ne%*4-1
  150 DIM bf% ne%*64+15
  160 OSCLI("LOAD ws2812.bin &B0000")
  170 IF ?&B0000<>&C3 THEN PRINT "ws2812.bin nicht geladen!" : END
  180 CALL &B0004
  190 er%=0
  200 REM Muster: jedes Byte anders, damit Vertauschungen auffallen
  210 FOR i%=0 TO ne%-1
  220   ?(fb%+i%*4)=i% : ?(fb%+i%*4+1)=255-i%
  230   ?(fb%+i%*4+2)=(i%*7) AND 255 : ?(fb%+i%*4+3)=128
  240 NEXT
  250 PROCrun(2,255)
  260 PROCrun(2,100)
  270 PROCrun(1,255)
  280 PROCrun(2,0)
  290 PRINT
  300 IF er%=0 THEN PRINT "wstest: alles OK" ELSE PRINT "wstest: ";er%;" FEHLER"
  310 END
  320 :
  330 REM Ein Frame mit rp% LEDs je Eintrag und Helligkeit b% entpacken
  340 REM und den Bitpuffer vollstaendig gegen die Rechnung pruefen.
  350 REM Hinter dem erwarteten Ende muss der Fuellwert &5A stehen bleiben.
  360 DEF PROCrun(rp%,b%)
  370 LOCAL i%,r%,j%,n%,k%,s%,v%,p%,e%,mx%
  380 FOR i%=0 TO ne%*64+12 STEP 4 : !(bf%+i%)=&5A5A5A5A : NEXT
  390 !&B0008=fb% : !&B000C=bf% : !&B0010=ne%*4
  400 ?&B0014=rp% : ?&B0015=b%
  410 CALL &B0000
  420 k%=(b%*90) DIV 256
  430 e%=0 : mx%=0 : p%=bf%
  440 FOR i%=0 TO ne%-1
  450   FOR r%=1 TO rp%
  460     FOR j%=0 TO 3
  470       s%=(?(fb%+i%*4+j%)*k%) DIV 256
  480       IF s%>mx% THEN mx%=s%
  490       v%=0
  500       FOR n%=0 TO 7
  510         v%=v%*2
  520         IF ?p%=&10 THEN v%=v%+1 ELSE IF ?p%<>0 THEN e%=e%+1
  530         p%=p%+1
  540       NEXT
  550       IF v%<>s% THEN e%=e%+1
  560     NEXT
  570   NEXT
  580 NEXT
  590 FOR i%=0 TO 15
  600   IF ?(p%+i%)<>&5A THEN e%=e%+1
  610 NEXT
  620 PRINT "LEDs je Eintrag ";rp%;", Helligkeit ";b%;": max ";mx%;" -> ";
  630 IF e%=0 THEN PRINT "OK" ELSE PRINT "FEHLER ";e%
  640 er%=er%+e%
  650 ENDPROC
