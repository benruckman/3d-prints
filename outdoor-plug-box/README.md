# Outdoor plug junction box

Weather-resistant enclosure for mated NEMA 5-15 plugs (extension cord + Traeger, etc.).

## Build

```bash
cd outdoor-plug-box
python build.py
# → output/base.stl
# → output/lid.stl
```

```bash
python build.py --part base
python build.py --cord-slot-w 20
```

## Print settings

| Setting | Recommendation |
|---------|----------------|
| Material | PETG or ASA |
| Walls | 4+ perimeters |
| Infill | 20–30% |
| Orientation | Base open-side up; lid flat |

## Assembly

The floor slopes to a single drain hole at the **-X / -Y** corner. Mount the box so that corner points away from the direction water is likely to come from.

1. Lay mated plugs in the base.
2. Drop each cord into the top slot on the end wall (slots are open at the top — no need to thread through a hole).
3. Zip-tie cords into the floor channels near each end.
4. Silicone gasket in the lid groove + silicone around cord slots where they meet the lid.
5. Mount with tabs; keep the seam angled so water runs off. Orient the drain corner (-X, -Y) away from splash/rain exposure.

The floor slopes up toward the opposite corner (+X, +Y) so water runs to the single drain hole.
