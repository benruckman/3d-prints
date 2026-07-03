"""
Parametric camera case + over-the-monitor saddle mount
for the InnoMaker U30CAM-4K-S1 (38x38 mm USB board cam),
sitting on top of an Elo 2702L touch monitor.

All dimensions are in millimetres. The four values marked *VERIFY*
are the ones to confirm against the actual board/monitor before printing.
Change them here and re-run to regenerate the STL.
"""
from pathlib import Path
import numpy as np
import trimesh
from trimesh.creation import box, cylinder
from trimesh.transformations import rotation_matrix

# ---------------------------------------------------------------- PARAMETERS
# --- Camera board ---
BOARD        = 38.0     # board is 38 x 38 mm (known)
HOLE_SPACING = 32.0     # *VERIFY* corner mounting-hole pitch, centre-to-centre
LENS_D       = 16.0     # *VERIFY* lens barrel diameter
LENS_PROTRUDE= 10.0     # *VERIFY* how far the lens sticks up off the board (informational/clearance)

SCREW_PILOT  = 1.8      # M2 self-tapping pilot hole
BOSS_D       = 5.5      # mounting-post diameter
BOSS_H       = 3.5      # board stand-off from inner front face

# --- Camera pod (the box that holds the board) ---
CLR        = 0.6        # clearance around board inside pocket
WALL       = 2.6        # pod side-wall thickness
FRONT_T    = 2.2        # front face thickness (where the lens hole is)
POD_DEPTH  = 15.0       # pod depth front-to-back
TILT_DEG   = 8.0        # downward tilt of the camera

# --- Saddle mount (hooks over the monitor's top edge) ---
MOUNT_WALL    = 3.0     # thickness of the saddle plates
TOP_THICK     = 13.0    # measured ~0.5 inch (12.7mm) edge thickness on the Elo 2702L
FRONT_FLAP_H  = 22.0    # how far the front plate drops down the monitor face
BACK_FLAP_H   = 42.0    # how far the back plate drops (longer = more stable)

# ---------------------------------------------------------------- DERIVED
POCKET   = BOARD + 2 * CLR
POD_OUT  = POCKET + 2 * WALL
SLOT     = TOP_THICK + 0.8          # a touch of slack over the bezel
SADDLE_W = POD_OUT

parts = []

# ---------------------------------------------------------------- CAMERA POD
# Outer shell
outer = box(extents=(POD_OUT, POD_DEPTH, POD_OUT))
# Inner pocket (open back): leave FRONT_T at the front (+Y), hollow toward back
pocket_len = (POD_DEPTH - FRONT_T) + 1.0
pocket_cy  = (POD_DEPTH/2 - FRONT_T) - pocket_len/2
pocket = box(extents=(POCKET, pocket_len, POCKET))
pocket.apply_translation((0, pocket_cy, 0))
pod = outer.difference(pocket)

# Lens hole through the front face (cylinder along Y)
lens = cylinder(radius=(LENS_D + 1.5)/2, height=POD_DEPTH + 4)
lens.apply_transform(rotation_matrix(np.pi/2, (1, 0, 0)))  # Z-axis -> Y-axis
pod = pod.difference(lens)

# Four slotted mounting bosses standing off the inner front face.
# Slots run along the board's diagonals and accept any hole pitch ~32-36mm.
inner_front_y = POD_DEPTH/2 - FRONT_T
R1, R2 = 22.3, 25.8          # radial range from board centre (pitch 31.5-36.5)
def stadium(p1, p2, radius, height, y_center):
    """Capsule-ish prism in the X-Z plane between two points, extruded along Y."""
    p1 = np.array(p1); p2 = np.array(p2)
    d = p2 - p1; L = np.linalg.norm(d)
    phi = np.arctan2(d[1], d[0])          # angle in X-Z plane
    c1 = cylinder(radius=radius, height=height)
    c1.apply_transform(rotation_matrix(np.pi/2, (1, 0, 0)))
    c2 = c1.copy()
    c1.apply_translation((p1[0], y_center, p1[1]))
    c2.apply_translation((p2[0], y_center, p2[1]))
    b = box(extents=(L, height, 2*radius))
    b.apply_transform(rotation_matrix(-phi, (0, 1, 0)))
    mid = (p1 + p2) / 2
    b.apply_translation((mid[0], y_center, mid[1]))
    return c1.union(c2).union(b)

for sx in (-1, 1):
    for sz in (-1, 1):
        u = np.array([sx, sz]) / np.sqrt(2)          # diagonal unit vector
        pA, pB = u * R1, u * R2
        boss = stadium(pA, pB, BOSS_D/2, BOSS_H, inner_front_y - BOSS_H/2)
        pod = pod.union(boss)
        slot = stadium(pA, pB, SCREW_PILOT/2, BOSS_H + FRONT_T + 2,
                       inner_front_y - (BOSS_H + FRONT_T)/2 + 1)
        pod = pod.difference(slot)

# Tilt the pod downward and move it to the front of the saddle
pod.apply_transform(rotation_matrix(np.radians(-TILT_DEG), (1, 0, 0)))
flap_front_y = MOUNT_WALL                       # front plate occupies Y[0, MOUNT_WALL]
pod.apply_translation((0, flap_front_y + POD_DEPTH/2 - 2.0, -POD_OUT/2 - 1.0))
parts.append(pod)

# ---------------------------------------------------------------- SADDLE
# Top plate, rests on the monitor's top surface (Z just above 0)
top_len = TOP_THICK + 2*MOUNT_WALL
top_cy  = (MOUNT_WALL - (TOP_THICK + MOUNT_WALL)) / 2
top = box(extents=(SADDLE_W, top_len, MOUNT_WALL))
top.apply_translation((0, top_cy, MOUNT_WALL/2))
parts.append(top)

# Front flap (down the front of the monitor)
front = box(extents=(SADDLE_W, MOUNT_WALL, FRONT_FLAP_H))
front.apply_translation((0, MOUNT_WALL/2, -FRONT_FLAP_H/2))
parts.append(front)

# Back flap (down the back, longer)
back = box(extents=(SADDLE_W, MOUNT_WALL, BACK_FLAP_H))
back.apply_translation((0, -TOP_THICK - MOUNT_WALL/2, -BACK_FLAP_H/2))
parts.append(back)

# ---------------------------------------------------------------- COMBINE
model = trimesh.boolean.union(parts, engine='manifold')

# Sanity output
print("watertight:", model.is_watertight)
print("volume cm^3:", round(model.volume/1000, 1))
b = model.bounds
print("bounds (mm): X %.1f  Y %.1f  Z %.1f" % tuple(b[1]-b[0]))

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PROJECT_DIR / "output"

model.export(str(DEFAULT_OUTPUT / "camera-mount-elo2702l.stl"))
print("wrote", str(DEFAULT_OUTPUT / "camera-mount-elo2702l.stl"))
