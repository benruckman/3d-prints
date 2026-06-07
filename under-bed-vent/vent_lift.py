from __future__ import annotations

from pathlib import Path

import cadquery as cq

from constants import LIFT_HEIGHT, VENT_L, VENT_L_IN, VENT_W, VENT_W_IN

HEIGHT = LIFT_HEIGHT
TOP_T = 6.0
WALL = 4.0
FLOOR = 3.0
FLANGE = 8.0
PLATFORM_W = 200.0
DUCT_W = 90.0
DUCT_H = 36.0
DUCT_LEN = 100.0
# ── Split joint hardware (M3 screw + nut) ────────────────────────────────────
M3_CLEAR = 3.2
M3_NUT_AF = 5.5
M3_NUT_DEPTH = 4.0
SEAM_SCREW_Y = (-50.0, 0.0, 50.0)
SEAM_SCREW_Z = HEIGHT - TOP_T / 2  # through top plate
DUCT_MOUNT_Y = (-28.0, 28.0)
DUCT_PAD_T = 8.0

PRINT_BED = 256.0


def _platform_l() -> float:
    return VENT_L + 2 * FLANGE


def _bbox(part: cq.Workplane) -> tuple[float, float, float]:
    bb = part.val().BoundingBox()
    return bb.xlen, bb.ylen, bb.zlen


def _clip_x(model: cq.Workplane, x_min: float | None, x_max: float | None) -> cq.Workplane:
    bb = model.val().BoundingBox()
    x0 = bb.xmin - 1 if x_min is None else x_min
    x1 = bb.xmax + 1 if x_max is None else x_max
    cx = (x0 + x1) / 2
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=bb.zmin - 1)
        .center(cx, 0)
        .rect(x1 - x0, bb.ylen + 10)
        .extrude(bb.zlen + 2)
    )
    return model.intersect(cutter)


def _add_side_duct(
    shell: cq.Workplane, side: str, ol: float, ow: float, void_h: float
) -> cq.Workplane:
    side = side.lower()
    if side in ("long", "left", "right"):
        sign = -1 if side in ("left",) else 1
        x = sign * (ol / 2 + DUCT_LEN / 2)
        duct = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .transformed(offset=(x, 0, 0))
            .box(DUCT_LEN, DUCT_W, DUCT_H + WALL, centered=(True, True, False))
        )
        duct_void = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR + WALL)
            .transformed(offset=(x, 0, 0))
            .box(DUCT_LEN + ol, DUCT_W - 2 * WALL, DUCT_H - WALL, centered=(True, True, False))
        )
    else:
        sign = -1 if side in ("back",) else 1
        y = sign * (ow / 2 + DUCT_LEN / 2)
        duct = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .transformed(offset=(0, y, 0))
            .box(DUCT_W, DUCT_LEN, DUCT_H + WALL, centered=(True, True, False))
        )
        duct_void = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR + WALL)
            .transformed(offset=(0, y, 0))
            .box(DUCT_W - 2 * WALL, DUCT_LEN + ow, DUCT_H - WALL, centered=(True, True, False))
        )

    return shell.union(duct).cut(duct_void)


def _add_ribs(shell: cq.Workplane, ol: float, ow: float, void_h: float) -> cq.Workplane:
    rib_t = 2.5
    z0 = FLOOR
    rib_h = void_h - 1

    x_lines = [x for x in range(-int(ol / 2) + 20, int(ol / 2) - 19, 35) if abs(x) > VENT_L / 2 + 10]
    y_lines = [y for y in range(-int(ow / 2) + 20, int(ow / 2) - 19, 35) if abs(y) > VENT_W / 2 + 10]

    for x in x_lines:
        rib = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .transformed(offset=(x, 0, 0))
            .box(rib_t, ow - 2 * WALL, rib_h, centered=(True, True, False))
        )
        shell = shell.union(rib)

    for y in y_lines:
        rib = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .transformed(offset=(0, y, 0))
            .box(ol - 2 * WALL, rib_t, rib_h, centered=(True, True, False))
        )
        shell = shell.union(rib)

    return shell


def _make_duct_only(outlet_side: str, round_duct: float | None) -> cq.Workplane:
    """Separate side duct — bolts to the right plenum half."""
    side = outlet_side.lower()
    sign = -1 if side in ("left", "back") else 1
    mount_z = FLOOR + DUCT_H / 2

    if side in ("long", "left", "right"):
        shell = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .box(DUCT_LEN, DUCT_W, DUCT_H + WALL, centered=(False, True, False))
        )
        void = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR + WALL)
            .box(DUCT_LEN + 2, DUCT_W - 2 * WALL, DUCT_H - WALL, centered=(False, True, False))
        )
        flange = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .transformed(offset=(-8, 0, 0))
            .box(8, DUCT_W + 12, DUCT_H + WALL, centered=(False, True, False))
        )
        shell = shell.union(flange).cut(void)

        for y in DUCT_MOUNT_Y:
            shell = (
                shell.faces("<X")
                .workplane()
                .center(y, mount_z)
                .circle(M3_CLEAR / 2)
                .cutThruAll()
            )

        if round_duct:
            z = FLOOR + DUCT_H / 2
            ring = cq.Workplane("YZ").workplane(offset=DUCT_LEN).center(0, z).circle(round_duct / 2).extrude(sign * 22)
            bore = cq.Workplane("YZ").workplane(offset=DUCT_LEN).center(0, z).circle(round_duct / 2 - WALL).extrude(sign * 24)
            shell = shell.union(ring).cut(bore)
    else:
        shell = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .box(DUCT_W, DUCT_LEN, DUCT_H + WALL, centered=(True, False, False))
        )
        void = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR + WALL)
            .box(DUCT_W - 2 * WALL, DUCT_LEN + 2, DUCT_H - WALL, centered=(True, False, False))
        )
        flange = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .transformed(offset=(0, -8, 0))
            .box(DUCT_W + 12, 8, DUCT_H + WALL, centered=(True, False, False))
        )
        shell = shell.union(flange).cut(void)

        for x in DUCT_MOUNT_Y:
            shell = (
                shell.faces("<Y")
                .workplane()
                .center(x, mount_z)
                .circle(M3_CLEAR / 2)
                .cutThruAll()
            )

    return shell


def _make_lift(outlet_side: str, round_duct: float | None, *, include_duct: bool = True) -> cq.Workplane:
    ol = _platform_l()
    ow = PLATFORM_W
    void_h = HEIGHT - TOP_T - FLOOR

    shell = cq.Workplane("XY").box(ol, ow, HEIGHT, centered=(True, True, False))

    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR)
        .rect(VENT_L, VENT_W)
        .extrude(void_h + 0.5)
    )
    shell = shell.cut(cavity)
    shell = shell.faces("<Z").workplane().rect(VENT_L, VENT_W).cutThruAll()

    if include_duct:
        shell = _add_side_duct(shell, outlet_side, ol, ow, void_h)
        if round_duct:
            side = outlet_side.lower()
            if side in ("long", "left", "right"):
                sign = -1 if side in ("left",) else 1
                ax = sign * (ol / 2 + DUCT_LEN)
                z = FLOOR + DUCT_H / 2
                ring = cq.Workplane("YZ").workplane(offset=ax).center(0, z).circle(round_duct / 2).extrude(sign * 22)
                bore = cq.Workplane("YZ").workplane(offset=ax).center(0, z).circle(round_duct / 2 - WALL).extrude(sign * 24)
            else:
                sign = -1 if side in ("back",) else 1
                ay = sign * (ow / 2 + DUCT_LEN)
                z = FLOOR + DUCT_H / 2
                ring = cq.Workplane("XZ").workplane(offset=ay).center(0, z).circle(round_duct / 2).extrude(sign * 22)
                bore = cq.Workplane("XZ").workplane(offset=ay).center(0, z).circle(round_duct / 2 - WALL).extrude(sign * 24)
            shell = shell.union(ring).cut(bore)
    else:
        # Port in plenum wall for the separate duct piece
        side = outlet_side.lower()
        if side in ("long", "left", "right"):
            sign = -1 if side in ("left",) else 1
            x = sign * ol / 2
            wall_cut = (
                cq.Workplane("YZ")
                .workplane(offset=x)
                .center(0, FLOOR + (void_h + WALL) / 2)
                .rect(DUCT_W, void_h)
                .extrude(sign * WALL * 3)
            )
            shell = shell.cut(wall_cut)

    shell = _add_ribs(shell, ol, ow, void_h)
    return shell


def _solid_count(part: cq.Workplane) -> int:
    return len(part.val().Solids())


def _cut_x_hole(part: cq.Workplane, x0: float, x1: float, y: float, z: float, r: float) -> cq.Workplane:
    length = abs(x1 - x0)
    cutter = (
        cq.Workplane("YZ")
        .workplane(offset=min(x0, x1))
        .center(y, z)
        .circle(r)
        .extrude(length)
    )
    return part.cut(cutter)


def _prepare_split_body(body: cq.Workplane) -> cq.Workplane:
    """Cut bolt holes through the top plate before splitting."""
    for sy in SEAM_SCREW_Y:
        body = _cut_x_hole(body, -14, 14, sy, SEAM_SCREW_Z, M3_CLEAR / 2)
    return body


def _add_seam_screws(left: cq.Workplane, right: cq.Workplane) -> tuple[cq.Workplane, cq.Workplane]:
    """Nut traps on the left half (holes already cut through top plate)."""
    for y in SEAM_SCREW_Y:
        trap = (
            cq.Workplane("XY")
            .workplane(offset=HEIGHT - TOP_T)
            .center(-8, y)
            .polygon(6, M3_NUT_AF)
            .extrude(M3_NUT_DEPTH)
        )
        left = left.cut(trap)
    return left, right


def _add_duct_mounts(right: cq.Workplane, outlet_side: str) -> cq.Workplane:
    """Integrated pad on the outer wall — no floating bosses."""
    ol = _platform_l()
    side = outlet_side.lower()
    if side not in ("long", "left", "right"):
        return right

    sign = 1 if side not in ("left", "back") else -1
    x_face = sign * ol / 2
    mount_z = FLOOR + DUCT_H / 2

    pad = (
        cq.Workplane("XY")
        .workplane(offset=mount_z - (DUCT_H + WALL) / 2)
        .transformed(offset=(x_face + sign * DUCT_PAD_T / 2, 0, 0))
        .box(DUCT_PAD_T, DUCT_W + 16, DUCT_H + WALL, centered=(True, True, False))
    )
    right = right.union(pad)

    for y in DUCT_MOUNT_Y:
        right = _cut_x_hole(
            right,
            x_face - sign * 2,
            x_face + sign * (DUCT_PAD_T + 2),
            y,
            mount_z,
            M3_CLEAR / 2,
        )
        trap_x = x_face + sign * 2
        trap = (
            cq.Workplane("YZ")
            .workplane(offset=trap_x)
            .center(y, mount_z)
            .polygon(6, M3_NUT_AF)
            .extrude(sign * M3_NUT_DEPTH)
        )
        right = right.cut(trap)

    return right


def _join_split_halves(
    left: cq.Workplane, right: cq.Workplane, outlet_side: str
) -> tuple[cq.Workplane, cq.Workplane]:
    left, right = _add_seam_screws(left, right)
    right = _add_duct_mounts(right, outlet_side)
    return left, right


def _split_halves(model: cq.Workplane, outlet_side: str) -> tuple[cq.Workplane, cq.Workplane]:
    model = _prepare_split_body(model)
    left = _clip_x(model, None, 0)
    right = _clip_x(model, 0, None)
    return _join_split_halves(left, right, outlet_side)


def _print_size_label(part: cq.Workplane) -> str:
    x, y, z = _bbox(part)
    return f"{x:.0f} x {y:.0f} x {z:.0f} mm"


def export(
    output_dir: Path,
    outlet: str,
    round_duct: float | None,
    split: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ol = _platform_l()

    if split:
        # 3-piece split for 256 mm beds: plenum halves + separate duct
        body = _make_lift(outlet, round_duct, include_duct=False)
        left, right = _split_halves(body, outlet)
        duct = _make_duct_only(outlet, round_duct)

        lp = output_dir / "mattress_vent_lift_left.stl"
        rp = output_dir / "mattress_vent_lift_right.stl"
        dp = output_dir / "mattress_vent_lift_duct.stl"
        cq.exporters.export(left, str(lp))
        cq.exporters.export(right, str(rp))
        cq.exporters.export(duct, str(dp))

        print(f"Wrote {lp}  ({_print_size_label(left)})")
        print(f"Wrote {rp}  ({_print_size_label(right)})")
        print(f"Wrote {dp}  ({_print_size_label(duct)})")
        print("  Assembly:")
        print("    1. Left + right: line up at center seam, 3x M3 through top plate")
        print("    2. Duct: bolt flange to pad on right outer wall (2x M3)")
        print("  Hardware: 5x M3x16 screw + 5x M3 nut")
        for label, part in [("left", left), ("right", right), ("duct", duct)]:
            n = _solid_count(part)
            if n != 1:
                print(f"  WARNING: {label} has {n} disconnected solids — check slicer")
            x, y, z = _bbox(part)
            if max(x, y, z) > PRINT_BED:
                print(f"  WARNING: {label} exceeds {PRINT_BED:.0f} mm — lay flat on build plate")
    else:
        model = _make_lift(outlet, round_duct, include_duct=True)
        path = output_dir / "mattress_vent_lift.stl"
        cq.exporters.export(model, str(path))
        print(f"Wrote {path}  ({_print_size_label(model)})")

    print(f"  vent {VENT_L_IN:g} x {VENT_W_IN:g} in  lift={HEIGHT:.0f} mm  footprint {ol:.0f} x {PLATFORM_W:.0f} mm")
    print(f"  outlet={outlet}")
    if ol > PRINT_BED and not split:
        print(f"  NOTE: footprint exceeds {PRINT_BED:.0f} mm — re-run with --split")
