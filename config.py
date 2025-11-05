import math

# --- Display ---
W, H = 600, 480
BACKGROUND = (0, 0, 10)
STAR_COLOR = (240, 240, 255)
GRID_COLOR = (70, 90, 110)
TEXT_COLOR = (200, 200, 200)

# --- Starfield ---
NUM_STARS = 2000

# --- Gridlines ---
GRID_EVERY_DEG = 30
GRID_RES_DEG = 3

# --- Camera ---
FOV_DEG = 60.0
FOV_MIN, FOV_MAX = 20.0, 120.0

# --- Controls ---
YAW_SPEED_DEG = 90.0
PITCH_SPEED_DEG = 90.0
ZOOM_SPEED = 30.0

# --- Performance ---
FPS = 60
