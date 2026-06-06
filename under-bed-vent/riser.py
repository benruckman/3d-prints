from __future__ import annotations

from pathlib import Path

import cadquery as cq

HEIGHT = 76.0
LEG_D = 38.0
LEG_DEPTH = 14.0
BASE_D = 58.0
TOP_LIP = 2.0


def _make_riser() -> cq.Workplane:
    outer_r = BASE_D / 2
    cup_r = LEG_D / 2
    lip_r = cup_r + TOP_LIP

    body = (
        cq.Workplane("XY")
        .circle(outer_r)
        .workplane(offset=HEIGHT * 0.55)
        .circle(lip_r + 2)
        .loft(combine=True)
    )

    base = cq.Workplane("XY").circle(outer_r).extrude(3)
    body = body.union(base)

    body = (
        body.faces(">Z")
        .workplane()
        .circle(cup_r)
        .cutBlind(-(LEG_DEPTH + 1))
    )

    body = body.faces("<Z").workplane().circle(3).cutThruAll()
    return body


def export(output_dir: Path, height: float | None, leg_d: float | None) -> None:
    global HEIGHT, LEG_D, BASE_D
    if height is not None:
        HEIGHT = height
    if leg_d is not None:
        LEG_D = leg_d
        BASE_D = max(BASE_D, LEG_D + 20)

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "bed_riser.stl"
    cq.exporters.export(_make_riser(), str(path))
    print(f"Wrote {path}  (print 4x — one per bed corner)")
    print(f"  height={HEIGHT:.0f} mm  leg cup diameter={LEG_D:.0f} mm  base diameter={BASE_D:.0f} mm")
