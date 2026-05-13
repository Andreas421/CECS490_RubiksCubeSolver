import numpy as np

# Kociemba expects the cube string in this face order.
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]

# Physical cube orientation used by the scanner:
#
#         yellow (U)
# orange (L) blue (F) red (R) green (B)
#         white  (D)
#
# Scan the four side faces with yellow physically up.
# Scan yellow with blue at the bottom of the camera view.
# Scan white with blue at the top of the camera view.
COLOR_TO_FACE = {
    "yellow": "U",
    "red": "R",
    "blue": "F",
    "white": "D",
    "orange": "L",
    "green": "B",
}

FACE_TO_COLOR = {face: color for color, face in COLOR_TO_FACE.items()}

CUBE_COLORS = set(COLOR_TO_FACE.keys())

# Optional correction applied after capture and before creating the solver string.
# Use this only if a face is consistently scanned rotated relative to the convention above.
# Values must be 0, 90, 180, or 270 degrees clockwise.
FACE_ROTATIONS = {
    "U": 180,
    "R": 0,
    "F": 0,
    "D": 180,
    "L": 0,
    "B": 0,
}

# Camera/scanner settings.
CAMERA_INDEX = 0
BOX_SIZE = 180
MIN_COLOR_PIXELS = 150
FLIP_PREVIEW = True

# HSV color ranges. Red wraps around the HSV hue boundary, so it has two ranges.
COLOR_RANGES = {
    "red1": (np.array([0, 120, 70]), np.array([10, 255, 255])),
    "red2": (np.array([170, 120, 70]), np.array([180, 255, 255])),
    "green": (np.array([35, 80, 50]), np.array([85, 255, 255])),
    "blue": (np.array([90, 80, 50]), np.array([130, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255])),
    "orange": (np.array([10, 100, 100]), np.array([20, 255, 255])),
    "white": (np.array([0, 0, 180]), np.array([180, 70, 255])),
}
