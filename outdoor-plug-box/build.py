"""
Outdoor weather-resistant junction box for mated NEMA 5-15 plugs.

Usage:
    python build.py
    python build.py --part base
    python build.py --cord-slot-w 20
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PROJECT_DIR / "output"

# ── Internal cavity (fits mated NEMA 5-15 plug bodies) ───────────────────────
INTERNAL_L = 130.0
INTERNAL_W = 65.0
INTERNAL_H = 58.0

# ── Structure ────────────────────────────────────────────────────────────────
WALL = 3.0
LID_WALL = 3.0
LID_TOP_H = 4.0
LID_OVERLAP = 12.0
LID_CLEARANCE = 0.4
DRIP_OVERHANG = 4.0

# ── Sealing ──────────────────────────────────────────────────────────────────
GASKET_W = 2.5
GASKET_D = 2.0

# ── Cord entries (top slots — drop cord in from above, plug stays inside) ───
CORD_SLOT_W = 10.0
CORD_SLOT_DEPTH = 16.0

# ── Drainage floor (slopes to one corner — orient that corner downhill) ───────
DRAIN_X_SIGN = -1  # drain corner at -X; apex (high point) at +X
DRAIN_Y_SIGN = -1  # drain corner at -Y; apex (high point) at +Y
FLOOR_DRAIN_PEAK = 4.0
FLOOR_MARGIN = 3.0
DRAIN_HOLE_D = 8.0
DRAIN_CORNER_INSET = 0.5

# ── Mounting tabs ────────────────────────────────────────────────────────────
MOUNT_TAB_W = 14.0
MOUNT_TAB_H = 6.0
MOUNT_HOLE_D = 5.5

# ── Lid handle ───────────────────────────────────────────────────────────────
HANDLE_SPAN = 48.0
HANDLE_BAR_W = 12.0
HANDLE_BAR_H = 10.0
HANDLE_POST = 10.0
HANDLE_CLEARANCE = 14.0

OUTER_L = INTERNAL_L + 2 * WALL
OUTER_W = INTERNAL_W + 2 * WALL
BASE_H = WALL + INTERNAL_H


def _cut_cord_slots(base: cq.Workplane) -> cq.Workplane:
    """U-notch in each end wall, open at the top, for dropping cords in."""
    for x_sign in (-1, 1):
        x = x_sign * (INTERNAL_L / 2 + WALL / 2)
        slot = (
            cq.Workplane("XY")
            .workplane(offset=BASE_H + 0.01)
            .center(x, 0)
            .rect(WALL + 2, CORD_SLOT_W)
            .extrude(-(CORD_SLOT_DEPTH + 0.02))
        )
        base = base.cut(slot)
    return base


def _add_sloped_floor(base: cq.Workplane) -> cq.Workplane:
    """Sloped floor — high at the corner opposite the drain."""
    inner_l = INTERNAL_L - FLOOR_MARGIN
    inner_w = INTERNAL_W - FLOOR_MARGIN
    apex_x = -DRAIN_X_SIGN * (inner_l / 2 - 1)
    apex_y = -DRAIN_Y_SIGN * (inner_w / 2 - 1)
    floor = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .rect(inner_l, inner_w)
        .workplane(offset=FLOOR_DRAIN_PEAK)
        .center(apex_x, apex_y)
        .rect(0.01, 0.01)
        .loft(combine=True)
    )
    return base.union(floor)


def _cut_drain_hole(base: cq.Workplane) -> cq.Workplane:
    x = DRAIN_X_SIGN * (INTERNAL_L / 2 - DRAIN_CORNER_INSET)
    y = DRAIN_Y_SIGN * (INTERNAL_W / 2 - DRAIN_CORNER_INSET)
    hole = (
        cq.Workplane("XY")
        .workplane(offset=WALL + 0.5)
        .center(x, y)
        .circle(DRAIN_HOLE_D / 2)
        .extrude(-(WALL + 2))
    )
    return base.cut(hole)


def _make_base() -> cq.Workplane:
    base = cq.Workplane("XY").box(OUTER_L, OUTER_W, BASE_H, centered=(True, True, False))

    base = (
        base.faces(">Z")
        .workplane()
        .rect(INTERNAL_L, INTERNAL_W)
        .cutBlind(-INTERNAL_H)
    )

    base = _cut_cord_slots(base)
    base = _add_sloped_floor(base)
    base = _cut_drain_hole(base)

    groove_outer = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H - GASKET_D)
        .rect(OUTER_L - WALL, OUTER_W - WALL)
        .extrude(GASKET_D)
    )
    groove_inner = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H - GASKET_D - 0.01)
        .rect(INTERNAL_L + 0.4, INTERNAL_W + 0.4)
        .extrude(GASKET_D + 0.02)
    )
    base = base.cut(groove_outer.cut(groove_inner))

    slot_w = CORD_SLOT_W + 4
    slot_d = 3.0
    slot_depth = 3.0
    for x_sign in (-1, 1):
        x = x_sign * (INTERNAL_L / 2 - 12)
        channel = (
            cq.Workplane("XY")
            .workplane(offset=WALL + slot_depth)
            .center(x, 0)
            .rect(slot_w, slot_d)
            .extrude(slot_depth)
        )
        base = base.cut(channel)

    tab_y = OUTER_W / 2
    for y_sign in (-1, 1):
        tab = (
            cq.Workplane("XY")
            .center(0, y_sign * (tab_y + MOUNT_TAB_W / 2 - 1))
            .rect(OUTER_L * 0.55, MOUNT_TAB_W)
            .extrude(MOUNT_TAB_H)
        )
        tab = tab.faces(">Z").workplane().center(0, 0).circle(MOUNT_HOLE_D / 2).cutThruAll()
        base = base.union(tab)

    return base


def _make_lid() -> cq.Workplane:
    skirt_l = OUTER_L + 2 * LID_CLEARANCE
    skirt_w = OUTER_W + 2 * LID_CLEARANCE
    top_l = skirt_l + 2 * DRIP_OVERHANG
    top_w = skirt_w + 2 * DRIP_OVERHANG

    lid = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H)
        .box(top_l, top_w, LID_TOP_H, centered=(True, True, False))
    )

    skirt_outer = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H - LID_OVERLAP)
        .rect(skirt_l, skirt_w)
        .extrude(LID_OVERLAP)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H - LID_OVERLAP - 0.01)
        .rect(skirt_l - 2 * LID_WALL, skirt_w - 2 * LID_WALL)
        .extrude(LID_OVERLAP + 0.02)
    )
    lid = lid.union(skirt_outer.cut(skirt_inner))

    z_top = BASE_H + LID_TOP_H
    half_span = HANDLE_SPAN / 2

    for y in (-half_span, half_span):
        post = (
            cq.Workplane("XY")
            .workplane(offset=z_top)
            .center(0, y)
            .rect(HANDLE_POST, HANDLE_POST)
            .extrude(HANDLE_CLEARANCE)
        )
        lid = lid.union(post)

    handle = (
        cq.Workplane("XY")
        .workplane(offset=z_top + HANDLE_CLEARANCE)
        .center(0, 0)
        .rect(HANDLE_BAR_W, HANDLE_SPAN + HANDLE_POST)
        .extrude(HANDLE_BAR_H)
    )
    handle = handle.edges("|Z").fillet(2)
    lid = lid.union(handle)

    return lid


def export(part: str, output_dir: Path, cord_slot_w: float | None = None) -> None:
    global CORD_SLOT_W
    if cord_slot_w is not None:
        CORD_SLOT_W = cord_slot_w

    output_dir.mkdir(parents=True, exist_ok=True)

    if part in ("base", "both"):
        path = output_dir / "base.stl"
        cq.exporters.export(_make_base(), str(path))
        print(f"Wrote {path}")

    if part in ("lid", "both"):
        path = output_dir / "lid.stl"
        cq.exporters.export(_make_lid(), str(path))
        print(f"Wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Outdoor plug junction box builder")
    parser.add_argument(
        "--part",
        choices=("base", "lid", "both"),
        default="both",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--cord-slot-w",
        type=float,
        default=None,
        help="Width of top cord slot in mm (default 18)",
    )
    args = parser.parse_args()
    export(args.part, args.output_dir, cord_slot_w=args.cord_slot_w)


if __name__ == "__main__":
    main()
