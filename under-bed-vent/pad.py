from __future__ import annotations

from pathlib import Path

import cadquery as cq

from constants import LIFT_HEIGHT

HEIGHT = LIFT_HEIGHT
TOP_T = 6.0
TOP_SIZE = 90.0
BASE_SIZE = 72.0
WALL = 3.5


def _make_pad() -> cq.Workplane:
    shell = cq.Workplane("XY").box(TOP_SIZE, TOP_SIZE, HEIGHT, centered=(True, True, False))

    void_h = HEIGHT - TOP_T - 3
    shell = (
        shell.faces(">Z")
        .workplane()
        .rect(TOP_SIZE - 2 * WALL, TOP_SIZE - 2 * WALL)
        .cutBlind(-void_h)
    )

    inset = TOP_SIZE / 2 - WALL - 4
    post = 8.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            pillar = (
                cq.Workplane("XY")
                .workplane(offset=3)
                .center(sx * inset, sy * inset)
                .rect(post, post)
                .extrude(void_h)
            )
            shell = shell.union(pillar)

    flare = cq.Workplane("XY").rect(BASE_SIZE, BASE_SIZE).extrude(3)
    return shell.union(flare)


def export(output_dir: Path, count: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "mattress_pad.stl"
    cq.exporters.export(_make_pad(), str(path))
    print(f"Wrote {path}  (print {count}x)")
    print(f"  height={HEIGHT:.0f} mm  top={TOP_SIZE:.0f} mm sq")
