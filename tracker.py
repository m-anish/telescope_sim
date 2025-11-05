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
    """
    Rotates a 3D vector around the Y-axis (vertical axis).
    
    Args:
        v: 3D vector as tuple (x, y, z)
        a: Rotation angle in radians (positive = counterclockwise when looking down Y-axis)
    
    Returns:
        Rotated vector as tuple (x', y, z')
    
    The Y-coordinate remains unchanged. The X and Z coordinates are transformed
    using the standard 2D rotation matrix in the XZ-plane.
    """
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (ca * x + sa * z, y, -sa * x + ca * z)

def rotate_x(v, a):
    """
    Rotates a 3D vector around the X-axis (horizontal axis).
    
    Args:
        v: 3D vector as tuple (x, y, z)
        a: Rotation angle in radians (positive = counterclockwise when looking along +X-axis)
    
    Returns:
        Rotated vector as tuple (x, y', z')
    
    The X-coordinate remains unchanged. The Y and Z coordinates are transformed
    using the standard 2D rotation matrix in the YZ-plane.
    """
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (x, ca * y - sa * z, sa * y + ca * z)

def sph_to_vec(alt_deg, az_deg):
    """
    Converts spherical coordinates to a 3D Cartesian unit vector.
    
    Args:
        alt_deg: Altitude angle in degrees (elevation above horizon)
                 -90° = straight down, 0° = horizon, +90° = straight up
        az_deg: Azimuth angle in degrees (compass direction)
                0° = +X axis, 90° = +Z axis, 180° = -X axis, 270° = -Z axis
    
    Returns:
        Unit vector as tuple (x, y, z) on the surface of a unit sphere
    
    Coordinate system:
        - Y-axis points up (altitude)
        - X-axis points in the 0° azimuth direction
        - Z-axis points in the 90° azimuth direction
        - Forms a right-handed coordinate system
    """
    alt, az = deg2rad(alt_deg), deg2rad(az_deg)
    y = math.sin(alt)  # Vertical component (up/down)
    r = math.cos(alt)  # Radius in the horizontal XZ-plane
    x = r * math.cos(az)  # X component (0° azimuth direction)
    z = r * math.sin(az)  # Z component (90° azimuth direction)
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
        """
        Transforms a world-space vector to camera-space.
        
        This applies the inverse of the camera's orientation to world objects,
        making them appear to move opposite to the camera's rotation.
        
        Camera conventions:
        - Yaw: Rotation around Y-axis (horizontal panning)
          * Increasing yaw = camera rotates right
          * World appears to pan right-to-left
          * Range: 0-360° (0° = looking along +X axis)
        
        - Pitch: Rotation around X-axis (vertical tilting)
          * Increasing pitch = camera tilts up
          * World appears to pan upward
          * Range: -90° to +90° (-90° = straight down, +90° = straight up)
        
        Args:
            v: World-space 3D vector as tuple (x, y, z)
        
        Returns:
            Camera-space 3D vector as tuple (x', y', z')
        """
        # Apply yaw rotation with negative angle to create inverse camera rotation
        # This makes increasing yaw (camera rotating right) cause world to pan right-to-left
        vyaw = rotate_y(v, -deg2rad(self.yaw))
        
        # Apply pitch rotation with positive angle
        # This makes increasing pitch (camera tilting up) cause world to pan upward
        vcam = rotate_x(vyaw, deg2rad(self.pitch)) 
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
