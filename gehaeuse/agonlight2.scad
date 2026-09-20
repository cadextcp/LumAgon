// ============================================================
// AgonLight2 Rev B (Olimex) – vereinfachtes 3D-Modell
// + 5x7-cm-Lochrasterplatine (Pegelwandler 74AHCT125)
//
// Maße aus: github.com/OLIMEX/AgonLight2
//           HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.kicad_pcb
//
// Koordinaten: Ursprung = linke untere Platinenecke, mm.
//   x nach rechts, y nach hinten (y = 0: GPIO/UEXT-Seite,
//   y = AGON_D: Buchsenseite mit SD, USB, Audio, VGA, USB-C, Reset),
//   z = 0: Platinenunterseite.
// Einzeln öffnen zeigt beide Platinen nebeneinander.
// ============================================================

AGON_W = 106.05;
AGON_D = 64.87;
AGON_T = 1.6;

// Befestigungslöcher (3,3 mm, Pad 5,5 mm)
AGON_HOLE_D = 3.3;
AGON_HOLES  = [[3.3, 11.2], [102.8, 11.2], [14.5, 40.0], [102.8, 48.7]];

// x-Mitte der Buchsen an der Oberkante
AGON_SD_X    = 8.9;
AGON_USBA_X  = 27.6;
AGON_AUDIO_X = 43.6;
AGON_VGA_X   = 66.9;
AGON_USBC_X  = 90.0;
AGON_RESET_X = 100.8;

// VGA: Flansch liegt an der Platinenkante, D-Kragen ragt 6 mm heraus
AGON_VGA_Z = 5.0;          // Mitte D-Kragen über Platinenoberseite

// Lochraster 5 x 7 cm (PY-5CM*7CM)
PB_W = 70;
PB_D = 50;
PB_T = 1.2;
PB_HOLE_D = 2.0;
PB_HOLE_E = 3.0;           // Lochmitte vom Rand – bitte nachmessen!
PB_HOLES = [[PB_HOLE_E, PB_HOLE_E], [PB_W - PB_HOLE_E, PB_HOLE_E],
            [PB_HOLE_E, PB_D - PB_HOLE_E], [PB_W - PB_HOLE_E, PB_D - PB_HOLE_E]];

// ------------------------------------------------------------
module _box(x0, x1, y0, y1, z0, z1) {
    translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

module _cyl_y(x, y0, y1, z, d, fn = 32) {
    translate([x, y0, z]) rotate([-90, 0, 0]) cylinder(d = d, h = y1 - y0, $fn = fn);
}

module _box_header(x0, x1) {   // gewinkelter Wannenstecker, Öffnung nach -y
    color("#222") difference() {
        _box(x0, x1, -4.0, 4.7, 0, 8.9);
        _box(x0 + 1.2, x1 - 1.2, -4.1, 2.5, 1.2, 7.7);
    }
    color("gold") for (x = [x0 + 2.2 : 2.54 : x1 - 2.2], z = [3.0, 5.6])
        _box(x - 0.32, x + 0.32, -2.5, 3, z - 0.32, z + 0.32);
}

module agonlight2() {
    // Platine
    color("#c8102e") difference() {
        cube([AGON_W, AGON_D, AGON_T]);
        for (h = AGON_HOLES) translate([h[0], h[1], -1]) cylinder(d = AGON_HOLE_D, h = 5, $fn = 24);
    }
    color("gold") for (h = AGON_HOLES) translate([h[0], h[1], AGON_T]) difference() {
        cylinder(d = 5.5, h = 0.05, $fn = 24);
        translate([0, 0, -1]) cylinder(d = AGON_HOLE_D, h = 2, $fn = 24);
    }
    color("white") translate([8, 14, AGON_T]) linear_extrude(0.05)
        text("Agon light 2", size = 3.5, font = "Liberation Sans:style=Bold");

    translate([0, 0, AGON_T]) {
        // --- Buchsenseite (y = AGON_D) ---
        // microSD + Karte
        color("silver") _box(1.55, 16.25, 50.3, 64.83, 0, 1.9);
        color("#2a6fdb") _box(AGON_SD_X - 5.5, AGON_SD_X + 5.5, 52, 66.3, 0.5, 1.3);
        // USB-A (Tastatur)
        color("silver") difference() {
            _box(21.6, 33.6, 50.5, 64.8, 0, 7.0);
            _box(22.2, 33.0, 55, 65, 0.9, 6.1);
        }
        color("white") _box(22.6, 32.6, 56, 64.6, 2.6, 4.4);
        // Audio 3,5 mm
        color("#222") _box(38.8, 48.4, 52.9, 64.85, 0, 5.0);
        color("#222") _cyl_y(AGON_AUDIO_X, 64.85, 67.9, 2.5, 5.0);
        // VGA (DE-15, Slim)
        color("#1f3d8a") _box(AGON_VGA_X - 15.4, AGON_VGA_X + 15.4, 52, 64.9, 0, 10.5);
        color("silver") {
            _box(AGON_VGA_X - 15.4, AGON_VGA_X + 15.4, 64.9, 65.5, AGON_VGA_Z - 6.25, AGON_VGA_Z + 6.25);
            translate([AGON_VGA_X, 65.5, AGON_VGA_Z]) rotate([-90, 0, 0])
                linear_extrude(5.5) polygon([[-8.2, -4], [8.2, -4], [7.1, 4], [-7.1, 4]]);
            for (s = [-1, 1]) _cyl_y(AGON_VGA_X + s * 12.5, 65.5, 70.5, AGON_VGA_Z, 4.8, 6);
        }
        // USB-C (Strom + Seriell)
        color("silver") hull() for (x = [AGON_USBC_X - 4.47 + 1.6, AGON_USBC_X + 4.47 - 1.6])
            _cyl_y(x, 57.35, 65.0, 1.63, 3.26);
        // Reset-Taster (seitlich betätigt)
        color("#222") _box(97.1, 104.5, 58.2, 64.8, 0, 6.5);
        color("#666") _cyl_y(AGON_RESET_X, 64.8, 68.0, 3.5, 2.5);

        // --- GPIO-Seite (y = 0) ---
        _box_header(49.8, 100.6);                       // GPIO 2x17
        _box_header(28.7, 49.3);                        // UEXT 2x5
        color("ivory") _box(22.1, 28.2, -4.0, 2.4, 0, 6.0);   // Akku JST-PH

        // --- Fläche ---
        color("#222") _box(0.8, 9.0, 18.9, 34.1, 0, 9.0);      // ZDI
        color("#111") translate([30.9, 44.4, 0]) cylinder(d = 12, h = 8, $fn = 40); // Summer
        color("#222") translate([44.36 - 7, 28.08 - 7, 0]) cube([14, 14, 1.4]);   // eZ80F92
        color("#222") translate([20.87 - 9.2, 26.94 - 5.1, 0]) cube([18.4, 10.2, 1.2]); // SRAM
        color("#333") translate([72.81 - 3.5, 27.44 - 3.5, 0]) cube([7, 7, 1.0]);  // ESP32-PICO
        color("#222") translate([81.3, 38.9, 0]) cube([5.4, 7.6, 1.6]);            // CH340
    }
}

module perfboard_5x7() {
    color("#d9892b") difference() {
        cube([PB_W, PB_D, PB_T]);
        for (h = PB_HOLES) translate([h[0], h[1], -1]) cylinder(d = PB_HOLE_D, h = 5, $fn = 20);
    }
    color("#e8b070") for (i = [0 : 23], j = [0 : 17])
        translate([PB_W / 2 + (i - 11.5) * 2.54, PB_D / 2 + (j - 8.5) * 2.54, PB_T])
            cylinder(d = 1.6, h = 0.05, $fn = 8);
    // 74AHCT125 (DIP-14) als Platzhalter
    color("#222") translate([PB_W / 2 - 9.5, PB_D / 2 - 3.2, PB_T + 0.5]) cube([19, 6.4, 3.3]);
}

// Vorschau, wenn diese Datei direkt geöffnet wird
// (gehaeuse.scad setzt AGON_NO_PREVIEW und blendet das aus)
if (is_undef(AGON_NO_PREVIEW)) {
    agonlight2();
    translate([0, -PB_D - 25, 0]) perfboard_5x7();
}
