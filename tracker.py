import math
import pygame

# Import constants from config.py
import config

# --- Utility math ---
def deg2rad(d):
    """Converts degrees to radians."""
    return d * math.pi / 180.0

def clamp(x, a, b):
    """Clamps a value x between a and b."""
    return max(a, min(b, x))

def rotate_y(v, a):
    """Rotates a 3D vector v around the Y-axis by angle a (in radians)."""
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (ca * x + sa * z, y, -sa * x + ca * z)

def rotate_x(v, a):
    """Rotates a 3D vector v around the X-axis by angle a (in radians)."""
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (x, ca * y - sa * z, sa * y + ca * z)

def sph_to_vec(alt_deg, az_deg):
    """Converts spherical coordinates (altitude, azimuth in degrees) to Cartesian vector."""
    alt, az = deg2rad(alt_deg), deg2rad(az_deg)
    y = math.sin(alt)
    r = math.cos(alt)
    x = r * math.cos(az)
    z = r * math.sin(az)
    return (x, y, z)

# --- Projection ---
class Camera:
    """Represents the camera's position, orientation, and projection."""
    def __init__(self, fov_deg, w, h):
        self.yaw = 0.0  # Rotation around Y-axis
        self.pitch = 0.0 # Rotation around X-axis
        self.fov = fov_deg
        self.w, self.h = w, h
        self.update_focal()

    def update_focal(self):
        """Calculates the focal length based on FOV and screen height."""
        fov_rad = deg2rad(self.fov)
        self.focal = (self.h / 2.0) / math.tan(fov_rad / 2.0)

    def world_to_camera(self, v):
        """Transforms a world-space vector to camera-space."""
        # Apply rotations based on camera orientation
        vyaw = rotate_y(v, -deg2rad(self.yaw))
        vcam = rotate_x(vyaw, -deg2rad(self.pitch))
        return vcam

    def project(self, v):
        """Projects a camera-space vector onto the 2D screen."""
        x, y, z = v
        if z <= 0:  # Object is behind the camera
            return None
        # Perspective projection formula
        sx = (self.w / 2.0) + (x * self.focal) / z
        sy = (self.h / 2.0) - (y * self.focal) / z # Y is inverted in screen coordinates
        return (sx, sy, z)

# --- Gridline helpers ---
def build_longitude_line(lon_deg, res_deg=config.GRID_RES_DEG):
    """Builds a list of points for a line of longitude (constant azimuth)."""
    pts = []
    lat = -90.0
    while lat <= 90.0 + 1e-6:
        pts.append(sph_to_vec(lat, lon_deg))
        lat += res_deg
    return pts

def build_latitude_line(lat_deg, res_deg=config.GRID_RES_DEG):
    """Builds a list of points for a line of latitude (constant altitude)."""
    pts = []
    lon = 0.0
    while lon <= 360.0 + 1e-6:
        pts.append(sph_to_vec(lat_deg, lon))
        lon += res_deg
    return pts

def draw_grid(screen, cam, lines, color):
    """Draws a set of grid lines using the camera's projection."""
    for line in lines:
        proj_pts = []
        for v in line:
            vc = cam.world_to_camera(v)
            p = cam.project(vc)
            proj_pts.append(None if p is None else (p[0], p[1]))
        
        # Draw segments between projected points, handling None for breaks
        seg = []
        for p in proj_pts:
            if p is None:
                if len(seg) >= 2:
                    pygame.draw.aalines(screen, color, False, seg)
                seg = []
            else:
                seg.append(p)
        if len(seg) >= 2:
            pygame.draw.aalines(screen, color, False, seg)
