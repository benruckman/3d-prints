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
python build.py --cord-d 16
```

## Print settings

| Setting | Recommendation |
|---------|----------------|
| Material | PETG or ASA |
| Walls | 4+ perimeters |
| Infill | 20–30% |
| Orientation | Base open-side up; lid flat |

## Assembly

1. Lay mated plugs in the base, cords exiting each end.
2. Zip-tie cords into the floor channels near each end.
3. Silicone gasket in the lid groove + silicone around cord entries.
4. Mount with tabs; keep the seam angled so water runs off.
