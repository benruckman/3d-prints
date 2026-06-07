# Under-bed vent kit

Floor vent is **10×4 in** (hardcoded in `constants.py`).

## Side vent beside the bed — print this

Vent is at the **edge** of the bed. This pulls air up through the floor register and blows it **straight up** beside the mattress. No screws — base halves friction-fit together, riser press-fits into the base.

```bash
cd under-bed-vent
python build.py side-tower
python build.py side-tower --height 200   # shorter tower
```

| STL | Qty | Print orientation |
|-----|-----|-------------------|
| `side_tower_base_left.stl` | 1× | flat on bed |
| `side_tower_base_right.stl` | 1× | flat on bed |
| `side_tower_riser.stl` | 1× | **standing** (plug down) |

### Assembly

```
        ↑ air up (beside mattress)
        │
   ┌────┴────┐  riser — press into base
   ├─────────┤  base (2 halves over vent)
   ═══ vent ═══  floor
```

1. Place both base halves over the floor vent opening (grille off). Long edge of vent along the bed.
2. The **mattress-side edge** of the base (+Y in the model) faces the bed.
3. Press the **riser** down into the socket on the base. The plug crosses the center seam and holds both halves in place.

### In the room

```
  [mattress]
       │
       │  ↑ tower
  ═════╪═════  base on floor vent (at bed edge)
```

## Legacy: vent under the mattress

If the vent is directly under the mattress (not at the side), use `python build.py mattress --split` — see git history or older docs for screw-based assembly.

## Print settings

| Part | Material | Infill |
|------|----------|--------|
| Side tower | PETG | 30%+ |
| Corner pads (legacy) | PETG | 40%+ |
