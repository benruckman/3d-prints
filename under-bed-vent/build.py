"""
Build STLs for the under-bed vent kit.

Usage:
    python build.py mattress              # vent lift + corner pads (floor mattress)
    python build.py vent-lift [--outlet left] [--split]
    python build.py pad [--count 4]
    python build.py deflector [--outlet left] [--duct 100]
    python build.py riser [--height 64]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import deflector
import pad
import riser
import vent_lift
from constants import OUTLET_SIDES

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PROJECT_DIR / "output"


def main() -> None:
    parser = argparse.ArgumentParser(description="Under-bed vent kit builder")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"STL output directory (default: {DEFAULT_OUTPUT})",
    )
    sub = parser.add_subparsers(dest="part", required=True)

    p_mattress = sub.add_parser("mattress", help="Vent lift + corner pads for floor mattress")
    p_mattress.add_argument("--outlet", choices=OUTLET_SIDES, default="long")
    p_mattress.add_argument("--duct", type=float, default=None)
    p_mattress.add_argument("--split", action="store_true")
    p_mattress.add_argument("--pad-count", type=int, default=4)

    p_lift = sub.add_parser("vent-lift", help="Load-bearing vent platform")
    p_lift.add_argument("--outlet", choices=OUTLET_SIDES, default="long")
    p_lift.add_argument("--duct", type=float, default=None)
    p_lift.add_argument("--split", action="store_true")

    p_pad = sub.add_parser("pad", help="Level corner pads")
    p_pad.add_argument("--count", type=int, default=4)

    p_def = sub.add_parser("deflector", help="Low-profile floor deflector (framed beds)")
    p_def.add_argument("--outlet", choices=OUTLET_SIDES, default="long")
    p_def.add_argument("--duct", type=float, default=None)

    p_riser = sub.add_parser("riser", help="Bed frame leg risers")
    p_riser.add_argument("--height", type=float, default=None)
    p_riser.add_argument("--leg-d", type=float, default=None)

    args = parser.parse_args()

    if args.part == "mattress":
        vent_lift.export(args.output_dir, args.outlet, args.duct, args.split)
        pad.export(args.output_dir, args.pad_count)
    elif args.part == "vent-lift":
        vent_lift.export(args.output_dir, args.outlet, args.duct, args.split)
    elif args.part == "pad":
        pad.export(args.output_dir, args.count)
    elif args.part == "deflector":
        deflector.export(args.output_dir, args.outlet, args.duct)
    elif args.part == "riser":
        riser.export(args.output_dir, args.height, args.leg_d)


if __name__ == "__main__":
    main()
