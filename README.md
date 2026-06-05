# 3D Prints

Parametric 3D-printable models, generated with Python + [CadQuery](https://cadquery.readthedocs.io/).

## Outdoor plug junction box

Weather-resistant enclosure for a mated pair of standard US 3-prong (NEMA 5-15) plugs — e.g. an extension cord connected to a Traeger grill cord.

**Not waterproof.** With a silicone gasket in the lid groove and silicone around each cord entry, it is suitable for summer outdoor use under a cover/eave. Do not submerge or rely on it in driving rain without additional protection.

### Setup

```bash
pip install -r requirements.txt
```

### Generate STLs

```bash
python outdoor_plug_box.py
# → output/outdoor_plug_box_base.stl
# → output/outdoor_plug_box_lid.stl
```

Options:

```bash
python outdoor_plug_box.py --part base
python outdoor_plug_box.py --cord-d 16   # thicker Traeger cord jacket
```

### Print settings

| Setting | Recommendation |
|---------|----------------|
| Material | **PETG** or **ASA** (UV/heat resistant) |
| Walls | 4+ perimeters |
| Top/bottom | 5+ layers |
| Infill | 20–30% |
| Orientation | Base open-side up; lid flat on build plate |

### Assembly

1. Lay the mated plugs in the base with cords exiting each end.
2. Zip-tie cords in the internal slots for strain relief.
3. Pack the lid gasket groove with 3 mm silicone cord or a bead of silicone caulk.
4. Seal each cord entry with silicone (use the outer flare pocket).
5. Mount with tabs (screw or zip-tie to deck/post). **Mount with the lid seam horizontal or slightly angled so water runs off**, not directly into the joint.

### Adjusting dimensions

Edit the constants at the top of `outdoor_plug_box.py`:

- `INTERNAL_L/W/H` — cavity size if your plugs are larger than typical
- `CORD_D` — cord entry diameter
- `LID_OVERLAP` — how far the lid skirt covers the base walls
