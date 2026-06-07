"""
Side vent tower — floor vent beside the mattress, air exits upward.

Sits over the 10×4 in floor register at the bed edge, routes air up a vertical
duct next to the mattress. Press-fit base and riser (no screws).

Usage:
    python build.py side-tower
    python build.py side-tower --height 200
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

from constants import VENT_L, VENT_L_IN, VENT_W, VENT_W_IN

# ── Tower ────────────────────────────────────────────────────────────────────
TOWER_H = 150.0  # mm vertical rise beside mattress
RISER_W = 150.0  # mm duct beside mattress
RISER_L = 70.0  # mm along bed edge
OUTLET_FLARE = 0.0  # mm top lip

# ── Base ─────────────────────────────────────────────────────────────────────
WALL = 8.0
FLOOR = 8.0
FLANGE = 10.0
PLENUM_H = 32.0  # mm under riser socket

# ── Base split (256 mm bed) ────────────────────────────────────────────────────
SOCKET_CLEAR = 0.35
RISER_PLUG_H = 16.0  # plug spans seam to lock base halves

PRINT_BED = 256.0


def _base_size() -> tuple[float, float]:
    return VENT_L + 2 * FLANGE, VENT_W + 2 * FLANGE


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


def _make_base_shell() -> cq.Workplane:
    """Base plenum over the floor vent with riser socket at +Y (mattress side)."""
    ol, ow = _base_size()
    total_h = FLOOR + PLENUM_H

    shell = cq.Workplane("XY").box(ol, ow, total_h, centered=(True, True, False))

    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR)
        .rect(VENT_L, VENT_W)
        .extrude(PLENUM_H + 0.5)
    )
    shell = shell.cut(cavity)
    shell = shell.faces("<Z").workplane().rect(VENT_L, VENT_W).cutThruAll()

    # Riser socket at mattress-side (+Y) edge of plenum
    socket_y = ow / 2 - RISER_W / 2 - WALL
    socket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR)
        .center(0, socket_y)
        .rect(RISER_L, RISER_W)
        .extrude(PLENUM_H + 0.5)
    )
    shell = shell.cut(socket)

    # Open deck over socket so plenum air reaches the riser (no closed lid)
    deck_open = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR + PLENUM_H - 0.01)
        .center(0, socket_y)
        .rect(RISER_L - 2 * WALL, RISER_W - 2 * WALL)
        .extrude(WALL + 1)
    )
    shell = shell.cut(deck_open)

    return shell


def _split_base(base: cq.Workplane) -> tuple[cq.Workplane, cq.Workplane]:
    return _clip_x(base, None, 0), _clip_x(base, 0, None)


def _make_riser() -> cq.Workplane:
    """Vertical tower — press-fits into base socket, open bottom and top."""
    ol, ow = _base_size()
    socket_y = ow / 2 - RISER_W / 2 - WALL
    base_top = FLOOR + PLENUM_H
    total_h = TOWER_H + RISER_PLUG_H

    # Outer shell includes a hollow press-fit sleeve below the deck (open bottom)
    outer = cq.Workplane("XY").box(RISER_L, RISER_W, total_h, centered=(True, True, False))
    outer = outer.translate((0, 0, -RISER_PLUG_H))

    inner = (
        cq.Workplane("XY")
        .workplane(offset=-RISER_PLUG_H)
        .rect(RISER_L - 2 * WALL, RISER_W - 2 * WALL)
        .extrude(total_h + 2)
    )
    tower = outer.cut(inner)

    # Ensure bottom is fully open (no leftover floor from wall offset)
    tower = (
        tower.faces("<Z")
        .workplane()
        .rect(RISER_L - 2 * WALL, RISER_W - 2 * WALL)
        .cutThruAll()
    )

    # Open top (air exits upward)
    tower = (
        tower.faces(">Z")
        .workplane()
        .rect(RISER_L - 2 * WALL, RISER_W - 2 * WALL)
        .cutBlind(-(WALL + 2))
    )

    # Top flare — keeps air from deflecting sideways
    flare = (
        cq.Workplane("XY")
        .workplane(offset=TOWER_H - WALL)
        .rect(RISER_L + OUTLET_FLARE, RISER_W + OUTLET_FLARE)
        .extrude(WALL)
    )
    flare = (
        flare.faces(">Z")
        .workplane()
        .rect(RISER_L - 2 * WALL, RISER_W - 2 * WALL)
        .cutBlind(-(WALL + 1))
    )
    tower = tower.union(flare)

    tower = tower.translate((0, socket_y, base_top))
    return tower


def export(output_dir: Path, tower_h: float | None) -> None:
    global TOWER_H
    if tower_h is not None:
        TOWER_H = tower_h

    output_dir.mkdir(parents=True, exist_ok=True)
    base = _make_base_shell()
    left, right = _split_base(base)
    riser = _make_riser()

    lp = output_dir / "side_tower_base_left.stl"
    rp = output_dir / "side_tower_base_right.stl"
    tp = output_dir / "side_tower_riser.stl"
    cq.exporters.export(left, str(lp))
    cq.exporters.export(right, str(rp))
    cq.exporters.export(riser, str(tp))

    ol, ow = _base_size()
    print(f"Wrote {lp}  ({_bbox(left)[0]:.0f} x {_bbox(left)[1]:.0f} x {_bbox(left)[2]:.0f} mm)")
    print(f"Wrote {rp}  ({_bbox(right)[0]:.0f} x {_bbox(right)[1]:.0f} x {_bbox(right)[2]:.0f} mm)")
    print(f"Wrote {tp}  ({_bbox(riser)[0]:.0f} x {_bbox(riser)[1]:.0f} x {_bbox(riser)[2]:.0f} mm)")
    print(f"  vent {VENT_L_IN:g} x {VENT_W_IN:g} in  tower height {TOWER_H:.0f} mm")
    print("  Assembly: fit base halves on vent, press riser into socket (no screws)")
    print("  Place base over floor vent, mattress-side (+Y) faces the bed edge")
