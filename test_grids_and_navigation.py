"""
sky_horizon.py
Minimal Stellarium-like horizon view (Option A)

Features:
- Horizon-based camera (you stand on the ground; initial view alt=0°, az=90° = East)
- Arrow keys to pan (Left/Right = azimuth, Up/Down = altitude)
- Mouse wheel zoom
- Dimmed Alt/Az grid (rings + spokes) with labels
- Dimmed RA/Dec grid (fixed to the sky, rotates with sidereal time)
- Cardinal labels N/E/S/W on the horizon circle
- No mouse drag panning (you asked for arrow-key navigation)
"""

import pygame
import math
import datetime
import time
import sys
import csv
import json

# -------------------------
# Bright Star Catalog (RA in hours, Dec in degrees, Mag, Name)
# Source: common bright stars
# -------------------------
BRIGHT_STARS = [
    (6.752, -16.716, -1.46, "Sirius"),
    (14.261, 19.182, 0.03, "Arcturus"),
    (5.242, -8.201, 0.18, "Rigel"),
    (5.919, 7.407, 0.50, "Betelgeuse"),
    (18.615, 38.783, 0.03, "Vega"),
    (19.846, 8.868, 1.25, "Altair"),
    (7.655, 5.225, 0.38, "Procyon"),
    (9.222, -69.717, 0.61, "Canopus"),
    (5.278, 45.998, 0.08, "Capella"),
    (2.097, 29.090, 2.06, "Mirfak"),
    (3.408, 49.861, 1.90, "Algol"),
    (13.420, -11.161, 0.98, "Spica")
]

# -------------------------
# Config / Window
# -------------------------
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Viewer - Horizon Mode")
clock = pygame.time.Clock()

CX, CY = WIDTH // 2, HEIGHT // 2

# projection "focal length" (feel free to adjust)
focal = 800.0    # larger -> more zoomed-in
min_focal = 200.0
max_focal = 3000.0

# Observer (Dharamsala)
OBSERVER_LAT_DEG = 32.24
OBSERVER_LON_DEG = 76.32
observer_lat = math.radians(OBSERVER_LAT_DEG)

# Colors (dimmed)
BG = (6, 6, 10)
ALT_AZ_COLOR = (60, 140, 60)     # green-ish for alt/az
EQ_COLOR = (140, 60, 60)         # red-ish for equatorial grid
CARDINAL_COLOR = (220, 220, 220)
LABEL_COLOR = (200, 200, 200)

FONT = pygame.font.SysFont("Arial", 14)

# initial camera: alt=0° (horizon), az=90° (east)
cam_alt = 0.0
cam_az = math.radians(90.0)

# sensitivity
AZ_STEP = math.radians(2.0)     # per arrow key tick
ALT_STEP = math.radians(2.0)
ZOOM_STEP = 1.12                # wheel scale factor

# rendering params
ALT_RING_STEP_DEG = 15
AZ_SPOKE_STEP_DEG = 30
RA_HOUR_STEP = 1
DEC_PARALLEL_STEP = 15

FPS = 60

# -------------------------
# Time / Sidereal Time
# -------------------------
def utc_now_datetime():
    return datetime.datetime.utcnow()

def julian_date(dt):
    # Meeus algorithm; dt is UTC naive datetime
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second + dt.microsecond / 1e6
    # fraction of day
    D = day + (hour + minute / 60.0 + second / 3600.0) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    JD = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + D + B - 1524.5
    return JD

def gmst_from_jd(JD):
    # approximate GMST in radians (good for visualization)
    gmst_hours = (18.697374558 + 24.06570982441908 * (JD - 2451545.0)) % 24.0
    gmst_rad = gmst_hours * 15.0 * math.pi / 180.0
    return gmst_rad

def local_sidereal_time_radians(lon_deg):
    dt = utc_now_datetime()
    JD = julian_date(dt)
    gmst = gmst_from_jd(JD)
    lst = (gmst + math.radians(lon_deg)) % (2 * math.pi)
    return lst

# -------------------------
# Coordinate conversions
# -------------------------
def clamp(v, a, b):
    return max(a, min(b, v))

def radec_to_altaz(ra_rad, dec_rad, lst_rad, lat_rad):
    # HA = LST - RA
    ha = lst_rad - ra_rad
    # normalize HA to -pi..pi
    ha = (ha + math.pi) % (2*math.pi) - math.pi
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha)
    sin_alt = clamp(sin_alt, -1.0, 1.0)
    alt = math.asin(sin_alt)
    cos_alt = math.cos(alt)
    if abs(cos_alt) < 1e-12:
        az = 0.0
    else:
        cos_az = (math.sin(dec_rad) - math.sin(alt)*math.sin(lat_rad)) / (cos_alt * math.cos(lat_rad))
        sin_az = -math.cos(dec_rad) * math.sin(ha) / cos_alt
        cos_az = clamp(cos_az, -1.0, 1.0)
        az = math.atan2(sin_az, cos_az)
        if az < 0:
            az += 2*math.pi
    return alt, az

# Convert an Alt/Az pair (radians, alt in -pi/2..pi/2, az 0..2pi from North->East) to a 3D world vector.
# We'll use the convention:
#   x = cos(alt) * sin(az)
#   y = sin(alt)            (up)
#   z = cos(alt) * cos(az) (forward toward North when az=0)
def altaz_to_world_vec(alt, az):
    x = math.cos(alt) * math.sin(az)
    y = math.sin(alt)
    z = math.cos(alt) * math.cos(az)
    return (x, y, z)

# -------------------------
# Rotations: transform world vector into camera coordinates
# Steps:
#   v1 = rotate_y(world_v, -cam_az)   # yaw: bring camera az to world
#   v_cam = rotate_x(v1, cam_alt)     # pitch: tilt according to cam_alt
#
# After this, positive z (z_cam) points forward (into view). We project using z_cam > 0.
# Rotation math below uses right-handed rotations.
# -------------------------
def rot_y(v, a):
    x, y, z = v
    ca = math.cos(a)
    sa = math.sin(a)
    # rotate around world Y axis
    xr = ca * x + sa * z
    yr = y
    zr = -sa * x + ca * z
    return (xr, yr, zr)

def rot_x(v, a):
    x, y, z = v
    ca = math.cos(a)
    sa = math.sin(a)
    xr = x
    yr = ca * y - sa * z
    zr = sa * y + ca * z
    return (xr, yr, zr)

def world_to_camera(v_world, cam_az, cam_alt):
    # yaw by -cam_az (so point at az=cam_az comes to front)
    v1 = rot_y(v_world, -cam_az)
    # pitch by cam_alt (positive cam_alt looks upward)
    v_cam = rot_x(v1, cam_alt)
    return v_cam

# perspective projection onto screen
def project_perspective(v_cam, focal_px):
    x, y, z = v_cam
    # only project points in front of camera
    if z <= 1e-5:
        return None
    sx = CX + (focal_px * (x / z))
    sy = CY - (focal_px * (y / z))
    return (int(sx), int(sy))

# drawing helpers
def draw_text(txt, pos, color=LABEL_COLOR):
    surf = FONT.render(txt, True, color)
    screen.blit(surf, pos)

# -------------------------
# Grid drawing
# -------------------------
def draw_altaz_grid(cam_az, cam_alt, focal_px):
    # Altitude rings (every ALT_RING_STEP_DEG)
    for alt_deg in range(0, 90, ALT_RING_STEP_DEG):
        alt = math.radians(alt_deg)
        pts = []
        for az_deg in range(0, 360, 3):
            az = math.radians(az_deg)
            v_world = altaz_to_world_vec(alt, az)
            v_cam = world_to_camera(v_world, cam_az, cam_alt)
            p = project_perspective(v_cam, focal_px)
            if p:
                pts.append(p)
        if len(pts) > 1:
            pygame.draw.aalines(screen, ALT_AZ_COLOR, True, pts)
            # label: choose a point on the east side of the ring (close to screen right)
            # We'll pick the point with max x in camera coords
            best = None
            best_x = -1e9
            for az_deg in range(0, 360, 6):
                az = math.radians(az_deg)
                v_world = altaz_to_world_vec(alt, az)
                v_cam = world_to_camera(v_world, cam_az, cam_alt)
                p = project_perspective(v_cam, focal_px)
                if p:
                    if p[0] > best_x:
                        best_x = p[0]
                        best = p
            if best:
                label = f"{alt_deg}°"
                draw_text(label, (best[0]+6, best[1]-8))

    # Azimuth spokes
    for az_deg in range(0, 360, AZ_SPOKE_STEP_DEG):
        az = math.radians(az_deg)
        pts = []
        for alt_deg in range(0, 90, 1):
            alt = math.radians(alt_deg)
            v_world = altaz_to_world_vec(alt, az)
            v_cam = world_to_camera(v_world, cam_az, cam_alt)
            p = project_perspective(v_cam, focal_px)
            if p:
                pts.append(p)
        if len(pts) > 1:
            pygame.draw.aalines(screen, ALT_AZ_COLOR, False, pts)
            # put a small label near the outermost visible point (lowest alt)
            for alt_deg in range(0, 90, 1):
                alt = math.radians(alt_deg)
                v_world = altaz_to_world_vec(alt, az)
                v_cam = world_to_camera(v_world, cam_az, cam_alt)
                p = project_perspective(v_cam, focal_px)
                if p:
                    draw_text(f"{az_deg}°", (p[0]-10, p[1]-10))
                    break

def draw_radec_grid(cam_az, cam_alt, focal_px):
    # compute LST
    lst = local_sidereal_time_radians(OBSERVER_LON_DEG)
    # RA meridians (constant RA)
    for ra_hour in range(0, 24, RA_HOUR_STEP):
        ra = math.radians(ra_hour * 15.0)
        pts = []
        for dec_deg in range(-80, 81, 2):
            dec = math.radians(dec_deg)
            alt, az = radec_to_altaz(ra, dec, lst, observer_lat)
            v_world = altaz_to_world_vec(alt, az)
            v_cam = world_to_camera(v_world, cam_az, cam_alt)
            p = project_perspective(v_cam, focal_px)
            if p:
                pts.append(p)
        if len(pts) > 1:
            pygame.draw.aalines(screen, EQ_COLOR, False, pts)

    # Declination parallels
    for dec_deg in range(-60, 91, DEC_PARALLEL_STEP):
        dec = math.radians(dec_deg)
        pts = []
        for ra_deg in range(0, 360, 3):
            ra = math.radians(ra_deg)
            alt, az = radec_to_altaz(ra, dec, lst, observer_lat)
            v_world = altaz_to_world_vec(alt, az)
            v_cam = world_to_camera(v_world, cam_az, cam_alt)
            p = project_perspective(v_cam, focal_px)
            if p:
                pts.append(p)
        if len(pts) > 1:
            pygame.draw.aalines(screen, EQ_COLOR, False, pts)

def draw_cardinals(cam_az, cam_alt, focal_px):
    # Cardinal points on horizon (alt=0)
    for label, az_deg in [("N", 0), ("E", 90), ("S", 180), ("W", 270)]:
        alt = 0.0
        az = math.radians(az_deg)
        v_world = altaz_to_world_vec(alt, az)
        v_cam = world_to_camera(v_world, cam_az, cam_alt)
        p = project_perspective(v_cam, focal_px)
        if p:
            draw_text(label, (p[0]-6, p[1]-12), CARDINAL_COLOR)

def draw_bright_stars(cam_az, cam_alt, focal_px):
    lst = local_sidereal_time_radians(OBSERVER_LON_DEG)

    for ra_h, dec_deg, mag, name in BRIGHT_STARS:
        ra = math.radians(ra_h * 15.0)
        dec = math.radians(dec_deg)

        alt, az = radec_to_altaz(ra, dec, lst, observer_lat)
        if alt < math.radians(-5):  # below horizon slightly -> don't draw
            continue

        v_world = altaz_to_world_vec(alt, az)
        v_cam = world_to_camera(v_world, cam_az, cam_alt)
        p = project_perspective(v_cam, focal_px)
        if p:
            x, y = p
            # star brightness scaling
            size = max(1, int(6 - mag))  # simple brightness rule
            pygame.draw.circle(screen, (230, 230, 255), (x, y), size)
            draw_text(name, (x + size + 3, y - size - 3))

def draw_bright_stars_dict(stars, cam_az, cam_alt, focal_px):
    lst = local_sidereal_time_radians(OBSERVER_LON_DEG)

    for ra_deg, dec_deg, mag, name in stars:
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)

        alt, az = radec_to_altaz(ra, dec, lst, observer_lat)
        if alt < math.radians(-5):  # below horizon slightly -> don't draw
            continue

        v_world = altaz_to_world_vec(alt, az)
        v_cam = world_to_camera(v_world, cam_az, cam_alt)
        p = project_perspective(v_cam, focal_px)
        if p:
            x, y = p
            # star brightness scaling
            size = max(1, int(6 - mag))  # simple brightness rule
            pygame.draw.circle(screen, (230, 230, 255), (x, y), size)
            draw_text(name, (x + size + 3, y - size - 3))

def draw_constellations(constellations, cam_az, cam_alt, focal_px):
    lst = local_sidereal_time_radians(OBSERVER_LON_DEG)

    for const in constellations:
        for line in const["lines"]:
            (ra1_deg, dec1_deg), (ra2_deg, dec2_deg) = line
            ra1 = math.radians(ra1_deg)
            dec1 = math.radians(dec1_deg)
            ra2 = math.radians(ra2_deg)
            dec2 = math.radians(dec2_deg)

            alt1, az1 = radec_to_altaz(ra1, dec1, lst, observer_lat)
            alt2, az2 = radec_to_altaz(ra2, dec2, lst, observer_lat)

            v_world1 = altaz_to_world_vec(alt1, az1)
            v_cam1 = world_to_camera(v_world1, cam_az, cam_alt)
            p1 = project_perspective(v_cam1, focal_px)

            v_world2 = altaz_to_world_vec(alt2, az2)
            v_cam2 = world_to_camera(v_world2, cam_az, cam_alt)
            p2 = project_perspective(v_cam2, focal_px)

            if p1 and p2:
                pygame.draw.aaline(screen, (200, 200, 255), p1, p2)

def draw_messier_objects(messiers, cam_az, cam_alt, focal_px):
    lst = local_sidereal_time_radians(OBSERVER_LON_DEG)

    for messier_num, name, ra_deg, dec_deg, magnitude, obj_type, dim_major_deg, dim_minor_deg in messiers:
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)

        alt, az = radec_to_altaz(ra, dec, lst, observer_lat)
        if alt < math.radians(-5):  # below horizon slightly -> don't draw
            continue

        v_world = altaz_to_world_vec(alt, az)
        v_cam = world_to_camera(v_world, cam_az, cam_alt)
        p = project_perspective(v_cam, focal_px)
        if p:
            x, y = p
            pygame.draw.circle(screen, (255, 200, 200), (x, y), 4)
            draw_text(name, (x + 5, y - 5))

def draw_ephemeris_objects(ephem_objects, cam_az, cam_alt, focal_px):
    lst = local_sidereal_time_radians(OBSERVER_LON_DEG)

    for body_name, ra_deg, dec_deg in ephem_objects:
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)

        alt, az = radec_to_altaz(ra, dec, lst, observer_lat)
        if alt < math.radians(-5):  # below horizon slightly -> don't draw
            continue

        v_world = altaz_to_world_vec(alt, az)
        v_cam = world_to_camera(v_world, cam_az, cam_alt)
        p = project_perspective(v_cam, focal_px)
        if p:
            x, y = p
            pygame.draw.circle(screen, (200, 255, 200), (x, y), 5)
            draw_text(body_name, (x + 6, y - 6))

def load_bright_stars_dict(csv_path="data/hyg_stars_4_0mag.csv"):
    """
    Load bright stars from CSV file.
    
    Returns:
        List of tuples (ra_deg, dec_deg, magnitude, name)
    """
    stars = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ra = float(row['RA_deg'])
            dec = float(row['Dec_deg'])
            mag = float(row['Magnitude'])
            name = row['Name'].strip() if row['Name'] else None
            stars.append((ra, dec, mag, name))
    return stars

def load_constellations(json_path="data/constellations.json"):
    """
    Load constellation data from JSON file.
    
    Returns:
        List of constellation dictionaries with name and lines
    """
    with open(json_path, 'r') as file:
        constellations = json.load(file)
    return constellations

def load_ephemeris(json_path='data/ephemeris_2025_2030.json'):
    """
    Load the precomputed ephemeris JSON file.
    
    Returns:
        dict: contains 'start_date', 'step_days', and body coordinates.
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # Convert start_date to datetime
    data["start_date"] = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
    return data

def load_ephemeris_bodies(data):
    """
    Load the list of ephemeris bodies from a json formatted data object.

    Returns:
        List of body names (str) present in the ephemeris
    """
 
    # Bodies are all keys except 'start_date' and 'step_days'
    bodies = [key for key in data.keys() if key not in ("start_date", "step_days")]
    return bodies

def load_ephemeris_objects(json_path="data/ephemeris_2025_2030.json"):
    """
    Returns properly positioned ephemeris objects after loading JSON file
    and computing their RA/Dec for the current date.

    Returns:
        List of tuples (body_name, ra_deg, dec_deg)
    """
    ephem_data = load_ephemeris(json_path)
    bodies = load_ephemeris_bodies(ephem_data)
    now_utc = datetime.datetime.utcnow()
    ephem_objects = []
    for body in bodies:
        ra, dec = get_body_ra_dec(ephem_data, body, now_utc)
        ephem_objects.append((body, ra, dec))
    return ephem_objects

def load_messier_objects(json_path="data/messier.json"):
    """
    Load Messier objects from JSON file.
    
    Returns:
        List of tuples (messier_num, name, ra_deg, dec_deg, magnitude, type, dim_major_deg, dim_minor_deg)
    """
    # Type mapping from JSON abbreviations to full type names
    type_mapping = {
        "gc": "Globular Cluster",
        "oc": "Open Cluster", 
        "snr": "Supernova Remnant",
        "sfr": "Nebula",
        "pn": "Planetary Nebula",
        "s": "Spiral Galaxy",
        "e": "Elliptical Galaxy",
        "i": "Irregular Galaxy",
        "rn": "Reflection Nebula",
        "pos": "Asterism"
    }
    
    messiers = []
    with open(json_path, 'r') as file:
        data = json.load(file)
        for obj in data:
            m_num = obj['id']
            name = obj.get('name', '')  # Can be null in JSON
            ra = float(obj['ra'])
            dec = float(obj['dec'])
            mag = float(obj['mag'])
            obj_type = type_mapping.get(obj['type'], obj['type'])  # Map abbreviation to full name
            dim_major = obj.get('dim_major_deg')  # Can be null
            dim_minor = obj.get('dim_minor_deg')  # Can be null
            messiers.append((m_num, name, ra, dec, mag, obj_type, dim_major, dim_minor))
    return messiers

# --- Helper function for computing ephemeris body position---
def get_body_ra_dec(ephem_data, body_name, utc_datetime):
    """
    Get RA/Dec of a given body at a specific UTC datetime using linear interpolation.

    Args:
        ephem_data (dict): loaded ephemeris data from load_ephemeris().
        body_name (str): name of the body ('moon', 'mars', etc.).
        utc_datetime (datetime): UTC datetime.

    Returns:
        tuple: (ra_deg, dec_deg)
    """
    if body_name not in ephem_data:
        raise ValueError(f"Body '{body_name}' not found in ephemeris.")
    
    start = ephem_data["start_date"]
    step = ephem_data["step_days"][body_name]
    coords = ephem_data[body_name]

    delta_days = (utc_datetime - start).total_seconds() / 86400.0
    if delta_days < 0 or delta_days > (len(coords)-1)*step:
        raise ValueError("UTC datetime out of ephemeris range.")

    # Find indices for linear interpolation
    idx_lower = int(delta_days // step)
    idx_upper = min(idx_lower + 1, len(coords)-1)
    fraction = (delta_days - idx_lower*step) / step

    ra_lower, dec_lower = coords[idx_lower]
    ra_upper, dec_upper = coords[idx_upper]

    # Linear interpolation
    ra_interp = ra_lower + fraction * (ra_upper - ra_lower)
    dec_interp = dec_lower + fraction * (dec_upper - dec_lower)

    # Normalize RA to 0-360
    ra_interp = ra_interp % 360

    return ra_interp, dec_interp

# -------------------------
# Main loop
# -------------------------
def main():
    global cam_az, cam_alt, focal

    bright_stars = load_bright_stars_dict(csv_path="data/hyg_stars_4_0mag.csv")
    constellations = load_constellations(json_path="data/constellations.json")
    messiers = load_messier_objects(json_path="data/messier.json")
    ephemeris_objects = load_ephemeris_objects(json_path="data/ephemeris_2025_2030.json")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # mouse wheel for zoom
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    focal = min(max(focal * (ZOOM_STEP ** event.y), min_focal), max_focal)
                else:
                    focal = min(max(focal * (ZOOM_STEP ** event.y), min_focal), max_focal)

            # keyboard zoom +/- (optional)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    focal = min(max(focal * 1.1, min_focal), max_focal)
                if event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    focal = min(max(focal / 1.1, min_focal), max_focal)

        # keyboard-based pan
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            cam_az -= AZ_STEP
        if keys[pygame.K_RIGHT]:
            cam_az += AZ_STEP
        if keys[pygame.K_UP]:
            cam_alt += ALT_STEP
        if keys[pygame.K_DOWN]:
            cam_alt -= ALT_STEP

        # clamp altitude so you can't flip upside-down
        cam_alt = clamp(cam_alt, -math.radians(85.0), math.radians(85.0))

        # normalize cam_az into 0..2pi for numerical stability (not required)
        cam_az = cam_az % (2 * math.pi)

        # Draw frame
        screen.fill(BG)

        # Draw grids & cardinals
        draw_altaz_grid(cam_az, cam_alt, focal)
        draw_radec_grid(cam_az, cam_alt, focal)
        draw_cardinals(cam_az, cam_alt, focal)
        #draw_bright_stars(cam_az, cam_alt, focal)
        draw_bright_stars_dict(bright_stars, cam_az, cam_alt, focal)
        draw_constellations(constellations, cam_az, cam_alt, focal)
        draw_messier_objects(messiers, cam_az, cam_alt, focal)
        draw_ephemeris_objects(ephemeris_objects, cam_az, cam_alt, focal)
        
        # HUD: show some info top-left
        lst_rad = local_sidereal_time_radians(OBSERVER_LON_DEG)
        lst_deg = (lst_rad * 180.0 / math.pi) % 360.0
        lst_h = lst_deg / 15.0
        hud_lines = [
            f"Location: Dharamsala  lat {OBSERVER_LAT_DEG:.2f}° lon {OBSERVER_LON_DEG:.2f}°",
            f"Cam alt: {math.degrees(cam_alt):.1f}°   Cam az: {math.degrees(cam_az):.1f}° (0=N,90=E)",
            f"LST: {lst_h:.5f} h  ({lst_deg:.2f}°)",
            f"Zoom (focal): {focal:.0f} px",
            "Controls: Arrow keys pan | Mouse wheel zoom | +/- zoom"
        ]
        y = 6
        for line in hud_lines:
            surf = FONT.render(line, True, LABEL_COLOR)
            screen.blit(surf, (8, y))
            y += 18

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
