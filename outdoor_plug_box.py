"""
Outdoor weather-resistant junction box for mated NEMA 5-15 plugs.

Designed for an extension cord plugged into a Traeger (or similar) power cord,
left outside during summer use. Not waterproof — weather-resistant when assembled
with a silicone gasket and cord sealant.

Usage:
    python outdoor_plug_box.py                  # export base + lid STLs
    python outdoor_plug_box.py --part base
    python outdoor_plug_box.py --cord-d 16      # thicker cord
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq

# ── Internal cavity (fits mated NEMA 5-15 plug bodies) ───────────────────────
INTERNAL_L = 130.0  # mm, plug/cord axis (X)
INTERNAL_W = 65.0
INTERNAL_H = 58.0

# ── Structure ────────────────────────────────────────────────────────────────
WALL = 3.0
LID_WALL = 3.0
LID_TOP_H = 4.0
LID_OVERLAP = 12.0  # skirt depth covering base walls
LID_CLEARANCE = 0.4
DRIP_OVERHANG = 4.0  # lid top extends past walls to shed water

# ── Sealing ──────────────────────────────────────────────────────────────────
GASKET_W = 2.5
GASKET_D = 2.0

# ── Cord entries (one per end) ───────────────────────────────────────────────
CORD_D = 14.0  # 16 AWG SJT ~8.5 mm; 14 AWG outdoor ~11 mm — size up if needed
CORD_Z = 22.0  # hole center height above cavity floor
CORD_FLARE_D = 20.0  # outer flare for silicone bead

# ── Mounting tabs (zip tie or #10 screw) ─────────────────────────────────────
MOUNT_TAB_W = 14.0
MOUNT_TAB_H = 6.0
MOUNT_HOLE_D = 5.5

# ── Lid handle (bridge style — finger clearance underneath) ───────────────────
HANDLE_SPAN = 48.0
HANDLE_BAR_W = 12.0
HANDLE_BAR_H = 10.0
HANDLE_POST = 10.0
HANDLE_CLEARANCE = 14.0

OUTER_L = INTERNAL_L + 2 * WALL
OUTER_W = INTERNAL_W + 2 * WALL
BASE_H = WALL + INTERNAL_H


def _cord_hole_z_local() -> float:
    """Face-local Z for cord holes (face workplane is centered on each wall)."""
    absolute_z = WALL + CORD_Z
    return absolute_z - BASE_H / 2


def _make_base() -> cq.Workplane:
    wp = cq.Workplane("XY")

    # Main shell, origin at bottom center
    base = wp.box(OUTER_L, OUTER_W, BASE_H, centered=(True, True, False))

    # Cavity
    base = (
        base.faces(">Z")
        .workplane()
        .rect(INTERNAL_L, INTERNAL_W)
        .cutBlind(-INTERNAL_H)
    )

    z_local = _cord_hole_z_local()

    # Cord tunnels on left/right ends
    for face in ("<X", ">X"):
        base = (
            base.faces(face)
            .workplane(centerOption="CenterOfMass")
            .center(0, z_local)
            .circle(CORD_D / 2)
            .cutThruAll()
        )
        # External flare pocket for silicone seal around cord jacket
        base = (
            base.faces(face)
            .workplane(centerOption="CenterOfMass")
            .center(0, z_local)
            .circle(CORD_FLARE_D / 2)
            .cutBlind(-4)
        )

    # Gasket groove on top of walls
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

    # Floor zip-tie channels near each cord entry (internal only — no rim breach)
    slot_w = CORD_D + 6
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

    # Mounting tabs on front/back
    tab_y = OUTER_W / 2
    for y_sign in (-1, 1):
        tab = (
            cq.Workplane("XY")
            .center(0, y_sign * (tab_y + MOUNT_TAB_W / 2 - 1))
            .rect(OUTER_L * 0.55, MOUNT_TAB_W)
            .extrude(MOUNT_TAB_H)
        )
        tab = (
            tab.faces(">Z")
            .workplane()
            .center(0, 0)
            .circle(MOUNT_HOLE_D / 2)
            .cutThruAll()
        )
        base = base.union(tab)

    return base


def _make_lid() -> cq.Workplane:
    skirt_l = OUTER_L + 2 * LID_CLEARANCE
    skirt_w = OUTER_W + 2 * LID_CLEARANCE
    top_l = skirt_l + 2 * DRIP_OVERHANG
    top_w = skirt_w + 2 * DRIP_OVERHANG

    # Top plate (slightly domed via a small center bump — helps shed water)
    lid = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H)
        .box(top_l, top_w, LID_TOP_H, centered=(True, True, False))
    )

    # Skirt overlaps base walls
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


def export(part: str, output_dir: Path, cord_d: float | None = None) -> None:
    global CORD_D, CORD_FLARE_D
    if cord_d is not None:
        CORD_D = cord_d
        CORD_FLARE_D = CORD_D + 6

    output_dir.mkdir(parents=True, exist_ok=True)

    if part in ("base", "both"):
        path = output_dir / "outdoor_plug_box_base.stl"
        cq.exporters.export(_make_base(), str(path))
        print(f"Wrote {path}")

    if part in ("lid", "both"):
        path = output_dir / "outdoor_plug_box_lid.stl"
        cq.exporters.export(_make_lid(), str(path))
        print(f"Wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate outdoor plug junction box STLs")
    parser.add_argument(
        "--part",
        choices=("base", "lid", "both"),
        default="both",
        help="Which part(s) to export (default: both)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for STL files (default: output/)",
    )
    parser.add_argument(
        "--cord-d",
        type=float,
        default=None,
        help="Cord entry diameter in mm (default: 14)",
    )
    args = parser.parse_args()

    export(args.part, args.output_dir, cord_d=args.cord_d)


if __name__ == "__main__":
    main()
