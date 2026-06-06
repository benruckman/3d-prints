from __future__ import annotations

from pathlib import Path

import cadquery as cq

from constants import VENT_L, VENT_L_IN, VENT_W, VENT_W_IN

PLENUM_H = 40.0
WALL = 2.5
FLOOR = 2.5
FLANGE = 12.0
DUCT_W = 90.0
DUCT_H = 32.0
DUCT_LEN = 110.0


def _outer_size() -> tuple[float, float]:
    return VENT_L + 2 * FLANGE, VENT_W + 2 * FLANGE


def _make_deflector(outlet_side: str, round_duct: float | None) -> cq.Workplane:
    ol, ow = _outer_size()
    total_h = FLOOR + PLENUM_H + WALL
    side = outlet_side.lower()

    plenum = cq.Workplane("XY").box(ol, ow, total_h, centered=(True, True, False))

    if side in ("long", "left", "right"):
        sign = -1 if side in ("left",) else 1
        x = sign * (ol / 2 + DUCT_LEN / 2)
        duct = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR)
            .transformed(offset=(x, 0, 0))
            .box(DUCT_LEN, DUCT_W, DUCT_H + WALL, centered=(True, True, False))
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

    shell = plenum.union(duct)

    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR)
        .rect(VENT_L, VENT_W)
        .extrude(PLENUM_H + 1)
    )
    shell = shell.cut(cavity)

    if side in ("long", "left", "right"):
        sign = -1 if side in ("left",) else 1
        x = sign * (ol / 2 + DUCT_LEN / 2)
        duct_void = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR + WALL)
            .transformed(offset=(x, 0, 0))
            .box(DUCT_LEN + ol, DUCT_W - 2 * WALL, DUCT_H - WALL, centered=(True, True, False))
        )
    else:
        sign = -1 if side in ("back",) else 1
        y = sign * (ow / 2 + DUCT_LEN / 2)
        duct_void = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR + WALL)
            .transformed(offset=(0, y, 0))
            .box(DUCT_W - 2 * WALL, DUCT_LEN + ow, DUCT_H - WALL, centered=(True, True, False))
        )

    shell = shell.cut(duct_void)

    if round_duct:
        if side in ("long", "left", "right"):
            sign = -1 if side in ("left",) else 1
            ax = sign * (ol / 2 + DUCT_LEN)
            z = FLOOR + DUCT_H / 2
            ring = (
                cq.Workplane("YZ")
                .workplane(offset=ax)
                .center(0, z)
                .circle(round_duct / 2)
                .extrude(sign * 22)
            )
            bore = (
                cq.Workplane("YZ")
                .workplane(offset=ax)
                .center(0, z)
                .circle(round_duct / 2 - WALL)
                .extrude(sign * 24)
            )
        else:
            sign = -1 if side in ("back",) else 1
            ay = sign * (ow / 2 + DUCT_LEN)
            z = FLOOR + DUCT_H / 2
            ring = (
                cq.Workplane("XZ")
                .workplane(offset=ay)
                .center(0, z)
                .circle(round_duct / 2)
                .extrude(sign * 22)
            )
            bore = (
                cq.Workplane("XZ")
                .workplane(offset=ay)
                .center(0, z)
                .circle(round_duct / 2 - WALL)
                .extrude(sign * 24)
            )
        shell = shell.union(ring).cut(bore)

    for x, y in (
        (-ol / 2 + 8, -ow / 2 + 8),
        (ol / 2 - 8, -ow / 2 + 8),
        (-ol / 2 + 8, ow / 2 - 8),
        (ol / 2 - 8, ow / 2 - 8),
    ):
        shell = (
            shell.faces(">Z")
            .workplane()
            .center(x, y)
            .circle(2)
            .cutBlind(-FLOOR)
        )

    return shell


def export(output_dir: Path, outlet: str, round_duct: float | None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "vent_deflector.stl"
    cq.exporters.export(_make_deflector(outlet, round_duct), str(path))
    print(f"Wrote {path}")
    print(f"  vent {VENT_L_IN:g} x {VENT_W_IN:g} in ({VENT_L:.1f} x {VENT_W:.1f} mm)  outlet={outlet}")
    if round_duct:
        print(f"  round duct adapter diameter={round_duct:.0f} mm")
