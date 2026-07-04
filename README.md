# 3D Prints

Parametric 3D-printable models, generated with Python + [CadQuery](https://cadquery.readthedocs.io/).

## Setup

```bash
pip install -r requirements.txt
```

## Projects

| Folder | Description | Build |
|--------|-------------|-------|
| [`outdoor-plug-box/`](outdoor-plug-box/) | Weather-resistant outdoor plug enclosure | `python build.py` |
| [`under-bed-vent/`](under-bed-vent/) | Side vent tower — air blows up beside mattress | `python build.py side-tower` |
| [`ant-nest-reservoir/`](ant-nest-reservoir/) | Refillable water reservoir for the Slide Ant Nest (H1 Hub) | `python build.py` |

Each project has its own `build.py`, `output/` folder, and README.
