$fn = 100;

board_size = [38.11, 38.11];
board_size_wiggle = [1, 1];
board_wire_cutout_w = 18;
board_wire_cutout_h = 6;
board_thickness = 1.57;
bottom_of_board_to_js_3mm_h = 16.7;
js_3mm_d = 25.45;
board_hole_d = 3.3;
board_hole_wall_thickness = 2;
board_hole_spacing = [30.5, 30.5];
board_post_h = 3;

box_floor_h = 2;
box_wall_thickness = 1;

top_thickness = 2;
top_wiggle = 0.3;
top_standoff_wiggle_h = 0.1;
top_standoff_height = bottom_of_board_to_js_3mm_h - top_thickness - board_thickness - top_standoff_wiggle_h;
top_inner_offset_round_val = 10;

finger_wiggle = 0.3;

module box_floor_cutout_2d() {
    square(board_size + board_size_wiggle, center=true);
}

module box_floor_2d() {
    offset(box_wall_thickness) {
        box_floor_cutout_2d();
    }
}

module box_floor_3d() {
    linear_extrude(box_floor_h) {
        box_floor_2d();
    }
}

module holes_2d() {
translate([-board_hole_spacing.x, board_hole_spacing.y]/2)
    circle(d=board_hole_d);
translate(board_hole_spacing/2)
    circle(d=board_hole_d);
translate(-board_hole_spacing/2)
    circle(d=board_hole_d);
translate([board_hole_spacing.x, -board_hole_spacing.y]/2)
    circle(d=board_hole_d);
}

module standoffs_2d() {
    difference() {
        offset(board_hole_wall_thickness)
            holes_2d();
        holes_2d();
    }
}

module standoffs_3d() {
    translate([0, 0, box_floor_h]) {
        linear_extrude(board_post_h) {
            standoffs_2d();
        }
    }
}

module cutout_2d() {
    translate([0, -box_wall_thickness]) {
        square([board_wire_cutout_w, board_size.y + board_size_wiggle.y], center=true);
    }
}

box_3d_height_without_floor = bottom_of_board_to_js_3mm_h + board_post_h;
box_3d_height = box_3d_height_without_floor + box_floor_h;

module box_3d() {
    box_floor_3d();
    standoffs_3d();

    translate([0, 0, box_floor_h]) {
        linear_extrude(box_3d_height_without_floor) {
            difference() {
                box_floor_2d();
                square(board_size + board_size_wiggle, center=true);
                cutout_2d();
            }
        }
    }
}

module top_inner_2d() {
    difference() {
        offset(-top_inner_offset_round_val) {
            offset(top_inner_offset_round_val) {
                standoffs_2d();
                difference() {
                    offset(-top_wiggle) {
                        box_floor_cutout_2d();
                    }
                    offset(-2) {
                        box_floor_cutout_2d();
                    }
                }
            }
        }
        holes_2d();
    }
}

module top_outer_2d() {
    difference() {
        box_floor_2d();
        circle(d=js_3mm_d);
        holes_2d();
    }
}

module top_wire_finger_2d() {
    translate([0, -(board_size.y + board_size_wiggle.y + box_wall_thickness)/2]) {
        square(size=[board_wire_cutout_w - finger_wiggle, box_wall_thickness], center=true);
    }
}

module top_3d() {
    translate([0, 0, box_floor_h + box_3d_height_without_floor - top_thickness]) {
        linear_extrude(top_thickness) {
            top_inner_2d();
        }
        
        translate([0, 0, -top_standoff_height]) {
            linear_extrude(top_standoff_height) {
                standoffs_2d();
            }
        }

        translate([0, 0, top_thickness]) {
            linear_extrude(top_thickness) {
                top_outer_2d();
            }
        }

        finger_h = box_3d_height_without_floor - board_wire_cutout_h;
        translate([0, 0, top_thickness - finger_h ]) {
            linear_extrude(finger_h) {
                top_wire_finger_2d();
            }
        }
    }
}

module block_blank_3d() {
    translate([0, 0, box_floor_h]) {
        linear_extrude(100) {
            offset(top_wiggle) {
                box_floor_2d();
            }
        }
    }
}

handle_length = 114;
handle_width_small = 20;
handle_width_big = 57 + 15;
handle_height = 34;
handle_rotation = [8, 0, 0];
handle_cable_hole_d = 6.5;

module handle_spheroid_3d() {
    rotate(handle_rotation) {
        //#cube([handle_width_big, handle_length, handle_height], center=true);
        scale([0.9, 1, 0.7]) {
            hull() {
                translate([0, handle_length/2 - handle_width_big/2, handle_height/2 - handle_width_small/2]) {
                    sphere(d=handle_width_big);
                }
                translate([0, handle_width_small/2-handle_length/2, handle_width_small/2 - handle_height/2]) {
                     sphere(d=handle_width_small);
                }
            }
        }
    }
}

module handle_cavity_3d() {
    block_blank_3d();

    difference() {
        translate([0, -30, 2]) {
            scale([1, 1, 1] * 0.5) {
                handle_spheroid_3d();
            }
        }
        block_blank_3d();
    }
    
    rotate(handle_rotation) {
        rotate([95, 0, 0]) {
            translate([0, 7, -10]) {
                cylinder(d=handle_cable_hole_d, h = 100);
            }
        }
    }
}

module handle_3d() {
    difference() {
        translate([0, -22, 2]) {
            handle_spheroid_3d();
        }

        top_cut_square_size = [300, 300, 100];
        translate([0, 0, box_3d_height + top_thickness + top_cut_square_size.z/2]) {
            cube(top_cut_square_size, center=true);
        }
        
        handle_cavity_3d();
    }

    standoffs_3d();
}

module scene_3d() {
    printing = true;
    print_spacing = 10;

    box_3d();

    if(printing) {
        translate([board_size.x + box_wall_thickness * 2 + print_spacing, 0, box_3d_height + top_thickness]) {
            rotate([0, 180, 0]) {
                top_3d();
            }
        }
    } else {
        top_3d();
    }
}

//scene_3d();
handle_3d();