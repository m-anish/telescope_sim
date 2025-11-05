"""
view_inside_sphere_nosmooth.py

Visualize ~2000 random stars on the inside of a unit celestial sphere.
- 600×480 window
- Viewpoint at center of sphere
- Arrow keys: look around (yaw / pitch)
- + / − : zoom in/out (changes FOV)
- ESC: quit
- Pitch clamped to ±90°
- FOV ~60° default
- Grid lines every 30°
"""

import pygame
import math
import random

# ---------------- Config ----------------
W, H = 600, 480
BACKGROUND = (0, 0, 10)
STAR_COLOR = (240, 240, 255)
GRID_COLOR = (70, 90, 110)
TEXT_COLOR = (200, 200, 200)

NUM_STARS = 2000
GRID_EVERY_DEG = 30
GRID_RES_DEG = 3

FOV_DEG = 60.0
FOV_MIN, FOV_MAX = 20.0, 120.0

YAW_SPEED_DEG = 90.0
PITCH_SPEED_DEG = 90.0
ZOOM_SPEED = 30.0

FPS = 60

# ---------------- Utility math ----------------
def deg2rad(d): return d * math.pi / 180.0
def clamp(x, a, b): return max(a, min(b, x))

def rotate_y(v, a):
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (ca * x + sa * z, y, -sa * x + ca * z)

def rotate_x(v, a):
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (x, ca * y - sa * z, sa * y + ca * z)

def sph_to_vec(alt_deg, az_deg):
    alt, az = deg2rad(alt_deg), deg2rad(az_deg)
    y = math.sin(alt)
    r = math.cos(alt)
    x = r * math.cos(az)
    z = r * math.sin(az)
    return (x, y, z)

def random_sphere_points(n):
    pts = []
    for _ in range(n):
        z = random.uniform(-1.0, 1.0)
        az = random.uniform(0.0, 2.0 * math.pi)
        r = math.sqrt(1.0 - z * z)
        x = r * math.cos(az)
        y = r * math.sin(az)
        pts.append((x, y, z))
    return pts

# ---------------- Projection ----------------
class Camera:
    def __init__(self, fov_deg, w, h):
        self.yaw = 0.0
        self.pitch = 0.0
        self.fov = fov_deg
        self.w, self.h = w, h
        self.update_focal()

    def update_focal(self):
        fov_rad = deg2rad(self.fov)
        self.focal = (self.h / 2.0) / math.tan(fov_rad / 2.0)

    def world_to_camera(self, v):
        vyaw = rotate_y(v, -deg2rad(self.yaw))
        vcam = rotate_x(vyaw, -deg2rad(self.pitch))
        return vcam

    def project(self, v):
        x, y, z = v
        if z <= 0: return None
        sx = (self.w / 2.0) + (x * self.focal) / z
        sy = (self.h / 2.0) - (y * self.focal) / z
        return (sx, sy, z)

# ---------------- Gridline helpers ----------------
def build_longitude_line(lon_deg, res_deg=3):
    pts = []
    lat = -90.0
    while lat <= 90.0 + 1e-6:
        pts.append(sph_to_vec(lat, lon_deg))
        lat += res_deg
    return pts

def build_latitude_line(lat_deg, res_deg=3):
    pts = []
    lon = 0.0
    while lon <= 360.0 + 1e-6:
        pts.append(sph_to_vec(lat_deg, lon))
        lon += res_deg
    return pts

# ---------------- Main ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Inside Celestial Sphere - no smoothing")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    cam = Camera(FOV_DEG, W, H)
    stars = random_sphere_points(NUM_STARS)
    star_sizes = [random.choice((1, 1, 1, 2)) for _ in range(NUM_STARS)]

    longitudes = [build_longitude_line(lon, GRID_RES_DEG) for lon in range(0, 360, GRID_EVERY_DEG)]
    latitudes  = [build_latitude_line(lat, GRID_RES_DEG) for lat in range(-90, 90 + 1, GRID_EVERY_DEG)]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()

        # Direct rotation
        if keys[pygame.K_LEFT]:  cam.yaw += YAW_SPEED_DEG * dt
        if keys[pygame.K_RIGHT]: cam.yaw -= YAW_SPEED_DEG * dt
        if keys[pygame.K_UP]:    cam.pitch += PITCH_SPEED_DEG * dt
        if keys[pygame.K_DOWN]:  cam.pitch -= PITCH_SPEED_DEG * dt
        cam.pitch = clamp(cam.pitch, -90.0, 90.0)

        # Zoom
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]: cam.fov -= ZOOM_SPEED * dt
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]: cam.fov += ZOOM_SPEED * dt
        cam.fov = clamp(cam.fov, FOV_MIN, FOV_MAX)
        cam.update_focal()

        screen.fill(BACKGROUND)

        # Gridlines
        def draw_grid(lines):
            for line in lines:
                proj_pts = []
                for v in line:
                    vc = cam.world_to_camera(v)
                    p = cam.project(vc)
                    proj_pts.append(None if p is None else (p[0], p[1]))
                seg = []
                for p in proj_pts:
                    if p is None:
                        if len(seg) >= 2:
                            pygame.draw.aalines(screen, GRID_COLOR, False, seg)
                        seg = []
                    else:
                        seg.append(p)
                if len(seg) >= 2:
                    pygame.draw.aalines(screen, GRID_COLOR, False, seg)

        draw_grid(longitudes)
        draw_grid(latitudes)

        # Stars
        for i, v in enumerate(stars):
            vc = cam.world_to_camera(v)
            p = cam.project(vc)
            if not p: continue
            sx, sy, z = p
            r = star_sizes[i]
            pygame.draw.circle(screen, STAR_COLOR, (int(sx), int(sy)), r)

        # Center crosshair
        cx, cy = W // 2, H // 2
        pygame.draw.line(screen, (80, 80, 120), (cx - 8, cy), (cx + 8, cy), 1)
        pygame.draw.line(screen, (80, 80, 120), (cx, cy - 8), (cx, cy + 8), 1)

        hud = [
            f"Yaw: {cam.yaw:.1f}°  Pitch: {cam.pitch:.1f}°  FOV: {cam.fov:.1f}°",
            "Arrows: look around   +/-: zoom   Esc: quit"
        ]
        y = 8
        for line in hud:
            screen.blit(font.render(line, True, TEXT_COLOR), (8, y))
            y += 20

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
