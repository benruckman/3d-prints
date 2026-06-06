# Under-bed vent kit

Fix a floor vent blocked by a twin mattress (no bed frame).

## Floor mattress — print this

**3× vent lift pieces + 4× corner pads** (all ~3 in tall). Every piece fits a **256 mm** bed when laid flat.

```bash
cd under-bed-vent
python build.py mattress --split
python build.py mattress --split --outlet left
```

| STL | Qty | Size (flat on bed) |
|-----|-----|--------------------|
| `mattress_pad.stl` | **4×** | 90 × 90 × 76 mm |
| `mattress_vent_lift_left.stl` | **1×** | 135 × 200 × 76 mm |
| `mattress_vent_lift_right.stl` | **1×** | 135 × 200 × 76 mm |
| `mattress_vent_lift_duct.stl` | **1×** | 105 × 98 × 40 mm |

**Assembly:** glue left + right at the center seam (alignment pegs built in), then glue the duct to the outer face of the right half. Lay every part **flat** (76 mm tall, not on end).

Or build parts individually:

```bash
python build.py vent-lift [--outlet left] [--split]
python build.py pad [--count 4]
```

## Bed with frame and legs

```bash
python build.py riser          # print 4×
python build.py deflector      # optional air router on floor vent
```

## Layout (floor mattress)

```
     [pad] ────────────── [pad]
        \                  /
         \  [vent lift]   /
        /                  \
     [pad] ────────────── [pad]
```

## Print settings

| Part | Material | Infill |
|------|----------|--------|
| Vent lift | PETG | 50%+ |
| Corner pads | PETG | 40%+ |
| Deflector | PETG | 20% |
| Bed risers | PETG | 40%+ |

Vent opening is hardcoded to **10×4 in** in `constants.py`.
