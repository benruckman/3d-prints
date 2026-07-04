"""
Water reservoir / hydration module for the "Slide Ant Nest" system (CanisMinor,
MakerWorld model 565369). Connects to a Nest Hub (H1) port using the *real*
"Connection Cap - M" dovetail geometry (imported from vendor/connection-cap-m.step)
so the fit is guaranteed.

Coordinate frame (mm)
---------------------
* X : length, projecting straight OUT from the hub (0 = wall against the hub)
* Y : vertical                          (0 = table top, ant passage centred at Y=12.5)
* Z : width, one module wide            (0 = the connected port, centred)

The reservoir connects on its SHORT end and lies low/horizontal, sticking straight
out from a single hub port so the other ports on that side stay free.

Design (wick-fed reservoir, sliding glass lid)
----------------------------------------------
* The main box is an open WATER reservoir. A single 75 x 25 mm glass microscope
  slide slides into side grooves as the whole top lid - slide it out to refill or
  to watch the ants. The body is widened to 27.5 mm to host the grooves.
* At the connector end is a shallow DRINKING DISH with a fused GRATE (ants drink
  without drowning). The grate sits below the nest passage so it never blocks the
  entrance.
* Reservoir and dish are separated by a divider wall with a LOW FEED HOLE at water
  level. You plug the hole with cotton / sponge; water wicks straight across into the
  cotton well and the basin under the grate. The cotton regulates the flow (the
  reservoir is open, so a snug plug + modest fill level keep the dish from over-
  filling).

Parts
-----
* base      - reservoir + connector + drinking dish + fused grate (one print)
* assembly  - base + glass + hub (visual fit check only)
* You add:  a 75 x 25 mm glass slide (the lid) and a small sponge/cotton wick.

Usage
-----
    python build.py                 # base.stl
    python build.py --part base
    python build.py --part assembly # includes the hub + glass, to preview the fit
    python build.py --height 30     # taller tank (more water)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PROJECT_DIR / "output"
VENDOR = PROJECT_DIR / "vendor"
CAP_STEP = VENDOR / "connection-cap-m.step"
HUB_STEP = VENDOR / "hub-body.step"

# ── Module interface (measured from the vendor STEP files) ───────────────────
PASSAGE_Y = 12.5          # centre height of the hub ant passage
PASSAGE_W = 9.0           # our tunnel width  (Z) - stays inside the hub's ~12.7
PASSAGE_H = 7.0           # our tunnel height (Y) - floor sits at 9.0
PASSAGE_FILLET = 1.5

# ── Sliding glass lid (standard 75 x 25 mm, ~1 mm microscope slide) ──────────
GLASS_L = 75.0          # slide length (covers the whole top)
GLASS_W = 25.0          # slide width
GLASS_T = 1.0           # slide thickness
GLASS_CLR = 0.5         # width clearance so it slides freely
GLASS_SPAN = GLASS_W + GLASS_CLR    # groove-to-groove span (25.5)
GLASS_ENGAGE = 2.0      # how far each glass edge sits into the side-wall groove
GLASS_SLOT = GLASS_T + 0.4          # groove height (glass + vertical clearance)
LID_LIP = 1.6           # retaining lip of wall above the glass slot

# ── Tank shell (widened to host the glass grooves) ───────────────────────────
FOOT_Z = 27.5           # outer width: 25 mm slide + 2 mm engagement + 1 mm lip / side
WALL = 3.0
FOOT_X = 78.0           # length: glass (75) covers dish->reservoir; +WALL far end
HEIGHT = 76.3           # total tank height (base 25.5 + 2 in for extra reservoir depth)
FLOOR = 2.5
# glass rides at the very top; everything else (grate/feed/passage) stays at the bottom
GLASS_BOT = HEIGHT - GLASS_SLOT - LID_LIP

# ── Drinking dish + wick divider ─────────────────────────────────────────────
VEST_X2 = 25.0          # far end of the drinking dish (X)
SHARE_W = 5.0           # divider wall between dish and reservoir
RES_X1 = VEST_X2 + SHARE_W          # reservoir interior starts here (X) = 30
WICK_W = 12.0           # width (Z) of the cotton feed hole through the divider
FEED_TOP = 11.0         # top of the low feed hole; cotton passes reservoir -> basin
                        # here at water level (cotton regulates the flow, see README)

# ── Drinking grate over the dish (below the passage so it can't block entry) ──
GRATE_SEAT = 6.0        # ledge the grate drops onto
GRATE_TH = 2.0          # grate thickness
GRATE_TOP = GRATE_SEAT + GRATE_TH   # 8.0, below the passage floor (9.0)
LEDGE_W = 2.0           # width of the ledge the grate rests on
SLOT_W = 0.8            # grate slot width
SLOT_PITCH = 2.5

# ── Recommended fill (for docs) ──────────────────────────────────────────────
FILL_MAX = GLASS_BOT - 3.0

# ── Connector transform (cap-local -> reservoir frame) ───────────────────────
CAP_ROT_AXIS = (0, 1, 0)
CAP_ROT_DEG = 180.0
CAP_SHIFT_X = 0.2


def _box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from explicit min/max corners (Y is vertical)."""
    return (
        cq.Workplane("XY")
        .transformed(offset=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        .box(x1 - x0, y1 - y0, z1 - z0)
    )


def _vcyl(r, x, z, y0, y1):
    """Vertical cylinder (axis +Y)."""
    return cq.Workplane().add(
        cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
    )


def _load_cap() -> cq.Workplane:
    cap = cq.importers.importStep(str(CAP_STEP))
    return cap.rotate((0, 0, 0), CAP_ROT_AXIS, CAP_ROT_DEG).translate((CAP_SHIFT_X, 0, 0))


def _passage_cutter(x0: float, x1: float) -> cq.Workplane:
    """Rounded-rect ant tunnel through X, centred on the port (Y=PASSAGE_Y, Z=0)."""
    return (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .center(PASSAGE_Y, 0.0)              # on YZ: local-x = Y, local-y = Z
        .rect(PASSAGE_H, PASSAGE_W)
        .extrude(x1 - x0)
        .edges("|X")
        .fillet(PASSAGE_FILLET)
    )


WELL_X = 19.0               # dish is open (no grate) from here to the divider: the
                            # "cotton well" where the wick drops down to the basin
RIB_X = (7.0, 12.0, 18.0)   # support ribs under the fused grate (X positions)


def _add_dish_supports(base: cq.Workplane) -> cq.Workplane:
    """Support ribs across the dish that carry the fused grate so it prints without
    trapped supports. Each rib has drain holes so the dish water stays connected."""
    zin = FOOT_Z / 2 - WALL
    for xc in RIB_X:
        base = base.union(_box(xc - 0.6, xc + 0.6, FLOOR, GRATE_SEAT, -zin, zin))
        for zc in (-5.0, 0.0, 5.0):   # flow holes through the rib
            base = base.cut(
                _box(xc - 1.0, xc + 1.0, FLOOR + 0.5, FLOOR + 2.5, zc - 1.5, zc + 1.5)
            )
    return base


def make_grate() -> cq.Workplane:
    """Grate covering the drinking dish; ants stand on it and drink through slots.
    Stops short of the divider (WELL_X) to leave the cotton well open, so the wick can
    drop past it into the basin. Fused into the base; rests on the ledge + support ribs."""
    x0, x1 = WALL + 0.3, WELL_X
    zo = (FOOT_Z / 2 - WALL) - 0.3
    grate = _box(x0, x1, GRATE_SEAT, GRATE_SEAT + GRATE_TH, -zo, zo)

    z = -zo + SLOT_PITCH
    while z < zo - 0.5:
        grate = grate.cut(
            _box(x0 + 2.5, x1 - 2.5, GRATE_SEAT - 0.5, GRATE_SEAT + GRATE_TH + 0.5,
                 z - SLOT_W / 2, z + SLOT_W / 2)
        )
        z += SLOT_PITCH
    return grate


def make_base() -> cq.Workplane:
    zin = FOOT_Z / 2 - WALL

    # Solid outer block
    base = _box(0, FOOT_X, 0, HEIGHT, -FOOT_Z / 2, FOOT_Z / 2)

    # Hollow the reservoir and the drinking dish (open top -> under the glass)
    base = base.cut(_box(RES_X1, FOOT_X - WALL, FLOOR, HEIGHT + 1, -zin, zin))
    base = base.cut(_box(WALL, VEST_X2, FLOOR, HEIGHT + 1, -zin, zin))

    # Trim the divider top to the glass underside so the slide passes over it.
    base = base.cut(_box(VEST_X2, RES_X1, GLASS_BOT, HEIGHT + 1, -zin, zin))
    # Low feed hole through the divider, at water level: cotton passes straight from
    # the reservoir into the basin/cotton well. The cotton regulates the flow.
    base = base.cut(
        _box(VEST_X2 - 0.1, RES_X1 + 0.1, FLOOR, FEED_TOP, -WICK_W / 2, WICK_W / 2)
    )

    # Glass channel: a groove in each side wall (with a retaining lip above) that runs
    # the full length and is OPEN AT BOTH ENDS, so the slide goes in / out either way -
    # no end stop, no entry-hole wall. The slide is held only by the two side rails.
    base = base.cut(                                    # the sliding slot, through both ends
        _box(0.0, FOOT_X + 1, GLASS_BOT, GLASS_BOT + GLASS_SLOT,
             -GLASS_SPAN / 2, GLASS_SPAN / 2)
    )
    base = base.cut(                                    # open the connector-end top
        _box(0.0, WALL, GLASS_BOT, HEIGHT + 1, -FOOT_Z / 2 - 1, FOOT_Z / 2 + 1)
    )
    base = base.cut(                                    # open the far-end top (drop the hole wall)
        _box(FOOT_X - WALL, FOOT_X + 1, GLASS_BOT, HEIGHT + 1, -FOOT_Z / 2 - 1, FOOT_Z / 2 + 1)
    )

    # Grate seat ledge (only under the grate; the cotton well WELL_X..VEST_X2 stays
    # open all the way to the basin floor so the wick can drop through)
    ledge_out = _box(WALL, WELL_X, GRATE_SEAT - 2.0, GRATE_SEAT, -zin, zin)
    ledge_in = _box(
        WALL + LEDGE_W, WELL_X + 0.1, GRATE_SEAT - 2.1, GRATE_SEAT + 0.1,
        -(zin - LEDGE_W), (zin - LEDGE_W),
    )
    base = base.union(ledge_out.cut(ledge_in))

    # Support ribs + the fused grate itself
    base = _add_dish_supports(base)
    base = base.union(make_grate())

    # Weld the connector on: a local boss bridging the cap mouth to the wall.
    # Kept within the cap-mouth footprint (Z +/-9, Y 1..22.5) so it stays inside the
    # hub port pocket and never clashes with the surrounding hub wall.
    base = base.union(_box(-1.0, WALL, 1.0, 22.5, -9.0, 9.0))
    base = base.union(_load_cap())

    # Ant tunnel through connector + wall into the dish (above the grate)
    base = base.cut(_passage_cutter(-7.0, WALL + 1.0))
    return base


def make_glass() -> cq.Workplane:
    """Representation of the bought 75 x 25 x 1 mm glass slide, seated in the channel.
    Not printed - shown in the assembly so you can see the fit."""
    return _box(WALL, WALL + GLASS_L, GLASS_BOT, GLASS_BOT + GLASS_T,
                -GLASS_W / 2, GLASS_W / 2)


def make_hub() -> cq.Workplane:
    # Pure translation that seats the hub's middle +X port onto our connector
    # (derived: T_view = T_mine . T_seat^-1 reduces to a translation, no rotation).
    hub = cq.importers.importStep(str(HUB_STEP))
    return hub.translate((-1.25, -0.62, -17.6))


def make_assembly() -> cq.Assembly:
    asm = cq.Assembly()
    asm.add(make_base(), name="base", color=cq.Color(0.85, 0.85, 0.9))
    asm.add(make_glass(), name="glass", color=cq.Color(0.6, 0.85, 0.95, 0.45))
    asm.add(make_hub(), name="hub", color=cq.Color(0.9, 0.7, 0.5))
    return asm


BUILDERS = {
    "base": make_base,
}


def export(part: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    names = list(BUILDERS) if part == "all" else [part] if part in BUILDERS else []

    for name in names:
        path = output_dir / f"{name}.stl"
        cq.exporters.export(BUILDERS[name](), str(path))
        print(f"Wrote {path}")

    if part in ("all", "assembly"):
        stl_path = output_dir / "assembly.stl"
        cq.exporters.export(make_assembly().toCompound(), str(stl_path))
        print(f"Wrote {stl_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ant nest water reservoir builder")
    parser.add_argument(
        "--part", choices=("all", "base", "assembly"), default="all"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--height", type=float, default=None, help="Tank height mm")
    parser.add_argument("--length", type=float, default=None,
                        help="Tank length projecting out from the hub, mm")
    args = parser.parse_args()

    global HEIGHT, FOOT_X, GLASS_BOT, FILL_MAX
    if args.height is not None:
        HEIGHT = args.height
        GLASS_BOT = HEIGHT - GLASS_SLOT - LID_LIP   # keep the glass at the top
        FILL_MAX = GLASS_BOT - 3.0
    if args.length is not None:
        FOOT_X = args.length

    export(args.part, args.output_dir)


if __name__ == "__main__":
    main()
