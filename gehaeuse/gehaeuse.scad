// ============================================================
// Gehäuse für AgonLight2 Rev B + 5x7-cm-Lochrasterplatine
// (LumAgon – Pegelwandler 74AHCT125 für die LED-Wand)
//
// Aufbau:
//   Unterteil  – Boden mit Abstandshaltern für beide Platinen,
//                Wände bis zur Oberkante der Agon-Platine
//   Deckel     – Wände + Decke, Buchsenausschnitte nach unten offen,
//                damit er über VGA, Audio und Reset gesetzt werden kann
//   6x M3x14 + M3-Mutter: Schraube von oben durch die Deckelsäule,
//   Mutter steckt unten in einer Sechskanttasche im Boden.
//   4 davon gehen durch die Agon-Löcher und klemmen die Platine,
//   2 durch die vorderen Eckpfosten.
//   Lochraster: 4x M2 (oder 2,2-mm-Blechschraube) in die Abstandshalter.
//
// Druck: PETG/PLA, 0,2 mm, ohne Stützen. Unterteil Boden nach unten,
// Deckel mit der Oberseite nach unten (part = "lid" dreht ihn schon).
// ============================================================

AGON_NO_PREVIEW = true;
include <agonlight2.scad>

/* [Ausgabe] */
part = "assembly"; // [assembly, base, lid, print_both, portwall_test, boards]
explode = 30;      // Deckelabstand in der Zusammenbauansicht

/* [Gehäuse] */
wall = 2.0;
floor_t = 2.4;
top_t = 2.0;
corner_r = 4;
gap = 2.0;           // Luft Platine–Wand
port_gap = 0.7;      // Luft Agon-Kante–Buchsenwand (VGA-Flansch liegt fast an)
standoff_h = 5.0;    // Platinen-Unterseite über Boden
clear_top = 20;      // Luft über der Agon-Oberseite
wire_gap = 22;       // Platz vor dem GPIO-Wannenstecker für Dupont-Stecker
hdr_overhang = 4.0;  // Wannenstecker ragen so weit über die Platinenkante
tol = 0.2;
lip_h = 2.0;         // Zentrierrand am Deckel
lip_t = 1.2;

/* [Lochrasterplatine 5x7] */
pb_front = 2;        // Abstand zur Vorderwand
pb_right = 10;       // Abstand zur rechten Innenwand
pb_pilot = 1.7;      // Kernloch für M2 / 2,2-mm-Blechschraube
pb_standoff_d = 5.0;

/* [Schrauben M3 + Mutter] */
screw_len = 14;      // Schaftlänge ohne Kopf (M3x14)
m3_clear = 3.4;
head_d = 6.4;        // Senkung für Zylinder-/Linsenkopf (ISO 4762 / 7380)
nut_s = 5.5;         // Schlüsselweite M3-Mutter (ISO 4032)
nut_h = 2.4;
nut_tol = 0.3;       // Luft in der Sechskanttasche
nut_pocket = 3.0;    // Taschentiefe von der Unterseite

/* [Extras] */
vents = true;
lid_text = true;
text1 = "AGON LIGHT 2";
text2 = "LumAgon";
cable_hole_d = 8;    // Kabel zur LED-Wand, halb im Unterteil, halb im Deckel
cable_hole_x = 18;
tie_anchor = true;   // Kabelbinder-Öse hinter dem Kabelloch

$fn = 48;

// ---------------- abgeleitete Maße ----------------
// Innenraum-Koordinaten: (0,0,0) = vordere linke Ecke auf dem Boden
AX = gap;
AY = pb_front + PB_D + wire_gap + hdr_overhang;
IW = gap + AGON_W + gap;
ID = AY + AGON_D + port_gap;
ZT = standoff_h + AGON_T;        // Trennebene = Agon-Oberseite
IH = ZT + clear_top;
PX = IW - pb_right - PB_W;
PY = pb_front;
POST = 9;

AGON_SCREWS = [for (h = AGON_HOLES) [AX + h[0], AY + h[1]]];
FRONT_POSTS = [[POST / 2, POST / 2], [IW - POST / 2, POST / 2]];
ALL_SCREWS  = concat(AGON_SCREWS, FRONT_POSTS);

// Mutter liegt oben in der Tasche, Schraubenspitze endet bündig mit ihrer Unterseite
NUT_TOP = -floor_t + nut_pocket;
HEAD_Z  = NUT_TOP - nut_h + screw_len;    // Auflage des Schraubenkopfs in der Deckelsäule
assert(HEAD_Z >= ZT + 4, "Schraube zu kurz: Kopf säße im schmalen Säulenfuß");
assert(HEAD_Z <= IH + top_t - 0.5, "Schraube zu lang für die Gehäusehöhe");

// Buchsenwand: [x auf der Platine, z-Mitte über Platinenoberseite, Breite, Höhe, Radius]
PORTS = [
    [AGON_SD_X,          0.9,        14.0,  3.6, 0.8],   // microSD
    [AGON_USBA_X,        3.5,        15.5,  8.5, 1.0],   // USB-A Tastatur
    [AGON_AUDIO_X,       2.6,         7.0,  7.0, 3.5],   // Audio
    [AGON_VGA_X,         AGON_VGA_Z, 20.5, 11.5, 2.0],   // VGA-Kragen
    [AGON_VGA_X - 12.5,  AGON_VGA_Z,  7.0,  7.0, 3.5],   // VGA-Schraubbolzen
    [AGON_VGA_X + 12.5,  AGON_VGA_Z,  7.0,  7.0, 3.5],
    [AGON_USBC_X,        1.65,       13.0,  7.5, 3.0],   // USB-C
    [AGON_RESET_X,       3.5,         6.5,  6.5, 3.25],  // Reset
];

echo(str("Außenmaß: ", IW + 2 * wall, " x ", ID + 2 * wall, " x ", floor_t + IH + top_t, " mm"));
echo(str("Schraubenkopf sitzt ", IH + top_t - HEAD_Z, " mm unter der Deckeloberfläche"));

// ---------------- Hilfsmodule ----------------
module rbox(w, d, h, r) {
    hull() for (x = [r, w - r], y = [r, d - r]) translate([x, y, 0]) cylinder(r = r, h = h);
}

module rrect_y(w, h, r, len) {   // abgerundetes Rechteck in xz, entlang +y
    rr = min(r, min(w, h) / 2 - 0.01);   // sonst verschwinden runde Löcher
    rotate([-90, 0, 0]) linear_extrude(len)
        offset(r = rr) offset(delta = -rr) square([w, h], center = true);
}

module post_shape(p, z0, z1, grow = 0) {   // Eckpfosten, mit der Wand verschmolzen
    hull() {
        translate([p[0], p[1], z0]) cylinder(d = POST + 2 * grow, h = z1 - z0);
        translate([p[0] < IW / 2 ? -1 : IW - POST / 2 - grow, -1, z0])
            cube([POST / 2 + 1 + grow, POST / 2 + 1 + grow, z1 - z0]);
    }
}

// Buchsenausschnitte; open_down = nach unten bis unter die Trennebene verlängert
module port_cuts(open_down) {
    for (p = PORTS) translate([AX + p[0], ID - 1, ZT + p[1]]) hull() {
        rrect_y(p[2], p[3], p[4], wall + 2);
        if (open_down) translate([0, 0, -p[1] - p[3] - 1]) rrect_y(p[2], p[3], p[4], wall + 2);
    }
    // Griffmulde vor der SD-Karte
    translate([AX + AGON_SD_X, ID + wall - 0.8, ZT + 0.9]) hull() {
        rrect_y(22, 9, 3, 2);
        if (open_down) translate([0, 0, -10]) rrect_y(22, 9, 3, 2);
    }
}

module nut_pocket() {   // Sechskant, Spitzen nach ±x
    translate([0, 0, -floor_t - 1])
        cylinder(d = (nut_s + nut_tol) / cos(30), h = nut_pocket + 1, $fn = 6);
}

module cable_cut() {
    translate([cable_hole_x, -wall - 1, ZT]) rotate([-90, 0, 0])
        cylinder(d = cable_hole_d, h = wall + 3);
}

// ---------------- Unterteil ----------------
module base() {
    difference() {
        union() {
            difference() {
                translate([-wall, -wall, -floor_t]) rbox(IW + 2 * wall, ID + 2 * wall, floor_t + ZT, corner_r);
                cube([IW, ID, ZT + 1]);
            }
            for (p = AGON_SCREWS) translate([p[0], p[1], -0.01]) cylinder(d = 8, h = standoff_h + 0.01);
            for (h = PB_HOLES) translate([PX + h[0], PY + h[1], -0.01])
                cylinder(d = pb_standoff_d, h = standoff_h + 0.01);
            for (p = FRONT_POSTS) post_shape(p, -0.01, ZT);
            if (tie_anchor) translate([cable_hole_x - 6, 9, -0.01]) difference() {
                cube([12, 7, 4]);
                translate([-1, 1.7, -1]) cube([14, 3.6, 3]);
            }
        }
        for (p = ALL_SCREWS) translate([p[0], p[1], 0]) {
            translate([0, 0, -floor_t - 1]) cylinder(d = m3_clear, h = ZT + floor_t + 2, $fn = 24);
            nut_pocket();
        }
        for (h = PB_HOLES) translate([PX + h[0], PY + h[1], 0.5]) cylinder(d = pb_pilot, h = standoff_h, $fn = 16);
        port_cuts(false);
        cable_cut();
    }
}

// ---------------- Deckel ----------------
module lip() {   // links, rechts, vorne; oberhalb der Trennebene mit der Wand verbunden
    difference() {
        union() {
            translate([tol, tol, ZT - lip_h]) cube([IW - 2 * tol, ID - 2 * tol, lip_h + 0.01]);
            translate([-0.01, -0.01, ZT]) cube([IW + 0.02, ID - tol, 2]);
        }
        translate([tol + lip_t, tol + lip_t, ZT - lip_h - 1]) cube([IW - 2 * tol - 2 * lip_t, ID, lip_h + 4]);
        for (p = FRONT_POSTS) post_shape(p, ZT - lip_h - 1, ZT + 0.01, tol);
    }
}

module vent_slots() {
    for (i = [0 : 5]) {
        y = AY + 18 + i * 4.5;
        hull() for (x = [AX + 30, AX + 85]) translate([x, y, IH - 1]) cylinder(d = 2, h = top_t + 2, $fn = 16);
    }
}

module lid_texts() {
    translate([IW / 2, 36, IH + top_t - 0.6]) linear_extrude(1)
        text(text1, size = 8, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
    translate([IW / 2, 22, IH + top_t - 0.6]) linear_extrude(1)
        text(text2, size = 6, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
}

module lid() {
    difference() {
        union() {
            difference() {
                translate([-wall, -wall, ZT]) rbox(IW + 2 * wall, ID + 2 * wall, IH + top_t - ZT, corner_r);
                translate([0, 0, ZT - 1]) cube([IW, ID, IH - ZT + 1]);
            }
            lip();
            // Säulen auf die Agon-Löcher: unten schmal (0603-Bauteile ab 3,7 mm vom Loch)
            for (p = AGON_SCREWS) translate([p[0], p[1], ZT]) {
                cylinder(d = 6, h = 1.5);
                translate([0, 0, 1.5]) cylinder(d1 = 6, d2 = 9, h = 1.5);
                translate([0, 0, 3]) cylinder(d = 9, h = IH - ZT - 3 + 0.01);
            }
            for (p = FRONT_POSTS) post_shape(p, ZT, IH + 0.01);
        }
        for (p = ALL_SCREWS) translate([p[0], p[1], 0]) {
            translate([0, 0, ZT - 1]) cylinder(d = m3_clear, h = IH + top_t - ZT + 2, $fn = 24);
            translate([0, 0, HEAD_Z]) cylinder(d = head_d, h = IH + top_t - HEAD_Z + 1, $fn = 32);
        }
        port_cuts(true);
        cable_cut();
        if (vents) vent_slots();
        if (lid_text) lid_texts();
    }
}

// ---------------- Druckteile ----------------
module base_print() { translate([wall, wall, floor_t]) base(); }
module lid_print()  { translate([wall, ID + wall, IH + top_t]) rotate([180, 0, 0]) lid(); }

module boards() {
    translate([AX, AY, standoff_h]) agonlight2();
    translate([PX, PY, standoff_h]) perfboard_5x7();
}

if (part == "base") base_print();
else if (part == "lid") lid_print();
else if (part == "print_both") { base_print(); translate([IW + 2 * wall + 10, 0, 0]) lid_print(); }
else if (part == "boards") boards();
else if (part == "portwall_test")
    translate([0, 0, ID + wall]) rotate([-90, 0, 0]) intersection() {
        union() { base(); lid(); }
        translate([-wall - 1, ID - 1, -floor_t - 1]) cube([IW + 2 * wall + 2, wall + 2, IH + floor_t + top_t + 2]);
    }
else {
    color("#3a3a3a") base();
    boards();
    color("#5a5a5a", 0.55) translate([0, 0, explode]) lid();
}
