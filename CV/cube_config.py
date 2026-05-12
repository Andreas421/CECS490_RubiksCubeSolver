import numpy as np

# Face mapping: white=U, yellow=D, green=F, blue=B, red=R, orange=L
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]

COLOR_MAP = {
    "white": "W",
    "orange": "O",
    "green": "G",
    "red": "R",
    "blue": "B",
    "yellow": "Y",
    "unknown": "X"
}

# Fixed cube housing orientation - changeable
COLOR_TO_FACE = {
    "white": "U",
    "yellow": "D",
    "green": "F",
    "blue": "B",
    "red": "R",
    "orange": "L"
}

# used to find which color face belongs to U, R, F, D, L, B - must change with above LUT
FACE_TO_COLOR = {
    "U": "white",
    "D": "yellow",
    "F": "green",
    "B": "blue",
    "R": "red",
    "L": "orange"
}

# Color Range LUT
# note: red1 & red2 are needed bc red wraps around hsv color space 0->10 & 170->180
color_ranges = {
    "red1": (np.array([0, 120, 70]), np.array([10, 255, 255])),
    "red2": (np.array([170, 120, 70]), np.array([180, 255, 255])),
    "green": (np.array([35, 80, 50]), np.array([85, 255, 255])),
    "blue": (np.array([90, 80, 50]), np.array([130, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255])),
    "orange": (np.array([10, 100, 100]), np.array([20, 255, 255])),
    "white": (np.array([0, 0, 180]), np.array([180, 70, 255]))
}

# Face rotation correction before building solver string
# Values are degrees clockwise: 0, 90, 180, or 270
# These are placeholders. Adjust after testing.
FACE_ROTATIONS = {
    "U": 180,
    "R": 0,
    "F": 0,
    "D": 180,
    "L": 0,
    "B": 180
}