# Gehäuse AgonLight2 + Pegelwandler (LumAgon)

Druckbares Gehäuse für den **AgonLight2 Rev B** und die **5 × 7 cm Lochrasterplatine** mit dem 74AHCT125.

| Datei | Inhalt |
|---|---|
| `agonlight2.scad` | Vereinfachtes 3D-Modell des AgonLight2 (Maße aus dem Olimex-KiCad-Layout) und der Lochrasterplatine. Direkt in OpenSCAD öffnen. |
| `gehaeuse.scad` | Parametrisches Gehäuse. `part` wählt die Ansicht bzw. das Druckteil. |
| `stl/gehaeuse_base.stl` | Unterteil, druckfertig |
| `stl/gehaeuse_lid.stl` | Deckel, druckfertig (liegt schon mit der Oberseite nach unten) |
| `stl/gehaeuse_portwall_test.stl` | Nur die Buchsenwand, als Passprobe (etwa 10 Minuten Druckzeit) |
| `stl/agonlight2_platinen.stl` | Beide Platinen als STL zum Einbinden in andere CAD-Programme |

**Außenmaß:** 114 × 148 × 31 mm

## Aufbau

- **Hinten:** Buchsenwand mit Ausschnitten für microSD (mit Griffmulde), USB-A, Audio, VGA (inkl. Schraubbolzen), USB-C und den Reset-Taster.
- **Innen hinten:** Der Agon liegt auf 4 Abstandshaltern (5 mm) unter seinen M3-Löchern.
- **Innen vorne:** Die Lochrasterplatine liegt auf 4 Abstandshaltern. Zwischen dem GPIO-Wannenstecker und der Lochrasterplatine bleiben 22 mm Platz für die Dupont-Stecker.
- **Vorne links:** Kabeldurchführung Ø 8 mm zur LED-Wand. Sie liegt zur Hälfte im Unterteil und zur Hälfte im Deckel, so passt das Kabel samt Stecker hinein. Dahinter sitzt eine Öse für einen Kabelbinder als Zugentlastung.
- **Trennebene** = Oberseite der Agon-Platine. Die Buchsenausschnitte im Deckel sind nach unten offen. Deshalb lässt sich der Deckel von oben aufsetzen, obwohl VGA, Audio und Reset über die Platinenkante hinausragen.
- **Verschraubung:** Die Schrauben kommen von oben durch die Deckelsäulen, gehen dann durch die Agon-Löcher und die Abstandshalter. Unten greifen sie in M3-Muttern, die in Sechskanttaschen im Boden stecken. Der Agon ist so zwischen Deckelsäule und Abstandshalter eingeklemmt. Zum Öffnen löst du die Schrauben von oben, das Gehäuse muss nicht umgedreht werden.

## Material

- 6 × **M3 × 14** Zylinder- oder Linsenkopf (ISO 4762 / ISO 7380). Der Kopf verschwindet 16,4 mm tief in der Deckelsäule. Du brauchst also einen Innensechskant- oder Torx-Schlüssel mit etwas Länge.
- 6 × **Mutter M3** (ISO 4032, SW 5,5). Drück sie vor dem Einbau von unten in die Sechskanttaschen. Sitzen sie zu locker, hält ein Tropfen Kleber. Klemmen sie zu stark, stellst du `nut_tol` größer.
- Eine andere Schraubenlänge stellst du über `screw_len` ein. Die Tiefe der Kopfsenkung rechnet das Modell dann selbst aus.
- 4 × **M2 × 6** (oder 2,2-mm-Blechschraube) für die Lochrasterplatine
- optional 4 Gummifüße

## Druck

PETG (wie die LED-Module) oder PLA, Schichthöhe 0,2 mm, 3 Wände, 15–20 % Infill. **Stützstrukturen sind nicht nötig.**

## Vor dem Druck bitte nachmessen

1. **Lochabstand der Lochrasterplatine.** Angenommen sind Bohrungen mit Ø 2 mm, deren Mitte 3 mm vom Rand liegt (Abstand 64 × 44 mm). Das Datenblatt nennt dazu keinen Wert. Weicht deine Platine ab, änderst du `PB_HOLE_E` in `agonlight2.scad`.
2. **Buchsenwand.** Die Höhen der Buchsen stammen aus den Bauteil-Datenblättern und nicht aus einer Messung. Drucke deshalb zuerst `gehaeuse_portwall_test.stl` und halte die Wand an den Agon. Passt ein Ausschnitt nicht, änderst du die Zeile in `PORTS` (in `gehaeuse.scad`): x-Position, z-Mitte über der Platine, Breite, Höhe, Radius.

## Wichtige Parameter (`gehaeuse.scad`)

| Parameter | Standard | Wirkung |
|---|---|---|
| `screw_len` | 14 | Länge der M3-Schrauben |
| `wire_gap` | 22 | Abstand GPIO-Stecker zur Lochrasterplatine |
| `clear_top` | 20 | Innenhöhe über dem Agon (für Bauteile auf der Lochrasterplatine) |
| `standoff_h` | 5 | Höhe der Abstandshalter |
| `cable_hole_d` / `cable_hole_x` | 8 / 18 | Kabeldurchführung vorne |
| `vents`, `lid_text`, `text1`, `text2` | an | Lüftungsschlitze und Gravur im Deckel |

STL neu erzeugen (OpenSCAD in der Kommandozeile):

```bash
openscad -o stl/gehaeuse_lid.stl -D 'part="lid"' gehaeuse.scad
```
