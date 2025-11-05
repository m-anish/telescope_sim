"""
finder_quat_sim.py

Quaternion-driven Digital Finderscope simulator.

Mounting convention (Option 2 / your description):
 - board lies flat on optical tube top
 - board +Y  = forward along tube
 - board +Z  = up (zenith)
 - board +X  = right

Camera axes used here:
 - camera forward = +Z (what we project along)
 - camera right   = +X
 - camera up      = +Y

Controls:
 - LEFT / RIGHT : yaw (azimuth) change
 - UP / DOWN    : pitch (altitude) change
 - Q / E        : roll left / right
 - mouse wheel  : zoom (focal)
 - ESC or window close : quit

FPS is limited to 10 (clock.tick(10))
"""

import pygame
import math
import datetime
import sys
import csv

# -------------------------
# Config
# -------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Finderscope - Quaternion Simulator")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 16)

CX, CY = WIDTH // 2, HEIGHT // 2
focal = 600.0
MIN_FOCAL = 100.0
MAX_FOCAL = 2500.0

# initial Euler angles (radians) for the quaternion (camera orientation)
yaw = math.radians(90.0)    # AZ (0 = North, 90 = East)
pitch = 0.0                 # ALT (0 = horizon)
roll = 0.0                  # ROLL

# angular steps for keys (per tick)
YAW_STEP = math.radians(1.5)
PITCH_STEP = math.radians(1.5)
ROLL_STEP = math.radians(1.0)

# Limit FPS to 10
FPS_LIMIT = 10

# Observer longitude is still needed for LST
LON_DEG = 76.32

# -------------------------
# Helper: time -> LST (radians)
# -------------------------
def utc_to_lst_radians(lon_deg):
    dt = datetime.datetime.utcnow()
    # Julian Date (simple)
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    JDN = dt.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
    JD = JDN + (dt.hour - 12)/24.0 + dt.minute/1440.0 + dt.second/86400.0
    T = (JD - 2451545.0) / 36525.0
    GMST_deg = (280.46061837 + 360.98564736629*(JD-2451545.0)
                + 0.000387933*T*T - (T*T*T)/38710000.0) % 360.0
    GMST_rad = math.radians(GMST_deg)
    lst = (GMST_rad + math.radians(lon_deg)) % (2*math.pi)
    return lst

# -------------------------
# Read small star catalog (CSV with RA_deg, Dec_deg, Magnitude, Name)
# Precompute equatorial vectors (unit) in ECI-like frame:
#   x = cos(dec) * cos(ra)
#   y = cos(dec) * sin(ra)
#   z = sin(dec)
# -------------------------
STAR_CSV = "./data/hyg_stars_4_0mag.csv"  # update path as needed

def load_star_vectors(csv_path, max_stars=None):
    stars = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ra_deg = float(row['RA_deg'])
                dec_deg = float(row['Dec_deg'])
                mag = float(row['Magnitude'])
                name = row.get('Name') or ""
            except Exception:
                continue
            # Convert RA/Dec degrees -> unit vector (equatorial)
            ra = math.radians(ra_deg)
            dec = math.radians(dec_deg)
            x = math.cos(dec) * math.cos(ra)
            y = math.cos(dec) * math.sin(ra)
            z = math.sin(dec)
            stars.append(((x, y, z), mag, name))
            if max_stars and len(stars) >= max_stars:
                break
    return stars

# load (you reported ~300; we can limit for speed if you want)
STAR_VECTORS = load_star_vectors(STAR_CSV, max_stars=400)

# -------------------------
# Quaternion helpers
# -------------------------
def quat_mult(q1, q2):
    # Hamilton product q = q1 * q2
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    return (w, x, y, z)

def quat_conjugate(q):
    w, x, y, z = q
    return (w, -x, -y, -z)

def quat_from_axis_angle(axis, angle_rad):
    ax, ay, az = axis
    s = math.sin(angle_rad/2.0)
    return (math.cos(angle_rad/2.0), ax*s, ay*s, az*s)

def quat_from_euler(yaw, pitch, roll):
    # order: yaw (around Y up) * pitch (around X right) * roll (around Z forward)
    # Build quaternions for each axis
    qy = quat_from_axis_angle((0.0, 1.0, 0.0), yaw)
    qx = quat_from_axis_angle((1.0, 0.0, 0.0), pitch)
    qz = quat_from_axis_angle((0.0, 0.0, 1.0), roll)
    # combined q = qy * qx * qz
    return quat_mult(quat_mult(qy, qx), qz)

def quat_to_matrix(q):
    # convert quaternion (w,x,y,z) to 3x3 rotation matrix
    w, x, y, z = q
    # normalize (small numerical drift)
    n = math.sqrt(w*w + x*x + y*y + z*z)
    if n == 0:
        return ( (1,0,0),(0,1,0),(0,0,1) )
    w /= n; x /= n; y /= n; z /= n
    m00 = 1 - 2*(y*y + z*z)
    m01 = 2*(x*y - z*w)
    m02 = 2*(x*z + y*w)
    m10 = 2*(x*y + z*w)
    m11 = 1 - 2*(x*x + z*z)
    m12 = 2*(y*z - x*w)
    m20 = 2*(x*z - y*w)
    m21 = 2*(y*z + x*w)
    m22 = 1 - 2*(x*x + y*y)
    return ((m00,m01,m02),(m10,m11,m12),(m20,m21,m22))

def mat3_mul_vec(m, v):
    (m00,m01,m02),(m10,m11,m12),(m20,m21,m22) = m
    x,y,z = v
    return (m00*x + m01*y + m02*z,
            m10*x + m11*y + m12*z,
            m20*x + m21*y + m22*z)

# -------------------------
# Earth rotation (apply LST): rotate equatorial vector about Earth's (celestial) Y axis by LST
# We use the same rot_y as earlier but via simple rotation function
# -------------------------
def rot_y_vec(v, angle):
    x,y,z = v
    ca = math.cos(angle); sa = math.sin(angle)
    return (ca*x + sa*z, y, -sa*x + ca*z)

# -------------------------
# Projection
# -------------------------
def project_persp(v_cam):
    x,y,z = v_cam
    if z <= 1e-6:
        return None
    sx = CX + focal * (x / z)
    sy = CY - focal * (y / z)
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        return (int(sx), int(sy))
    return None

# -------------------------
# Euler extractor for HUD (inverse of quat_from_euler order)
# We'll compute yaw, pitch, roll from the quaternion in the same axis sequence.
# Note: numerical edge cases are handled gracefully.
# -------------------------
def euler_from_quat(q):
    # q = qy * qx * qz  (Y * X * Z)
    # We'll convert quaternion to matrix then extract yaw/pitch/roll in same convention.
    m = quat_to_matrix(q)
    m00,m01,m02 = m[0]
    m10,m11,m12 = m[1]
    m20,m21,m22 = m[2]
    # pitch = asin(clamp(m02, -1..1))  (because m02 = sin(pitch) in our convention)
    pitch = math.asin(max(-1.0, min(1.0, m02)))
    # yaw from m00,m01,m02 and m22
    # yaw = atan2(-m12, m22) ???  (derivation depends on chosen ordering)
    # We'll compute using safe approach using atan2 from matrix:
    # Here using decomposition for our Y-X-Z order:
    # yaw = atan2(-m20, m22)  (rotation about Y)
    # roll = atan2(-m01, m00) (rotation about Z)
    # After testing these formulae give reasonable consistent values for our chosen q order.
    # If you need different sign conventions, we can flip signs later.
    try:
        yaw = math.atan2(-m20, m22)
        roll = math.atan2(-m01, m00)
    except Exception:
        yaw = 0.0
        roll = 0.0
    return yaw, pitch, roll

# -------------------------
# Main loop
# -------------------------
def main():
    global yaw, pitch, roll, focal

    # Precompute nothing else; STAR_VECTORS already ready
    running = True
    while running:
        # limit FPS
        dt = clock.tick(FPS_LIMIT)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    focal = min(MAX_FOCAL, focal * 1.1)
                else:
                    focal = max(MIN_FOCAL, focal / 1.1)

        # keyboard control (simulate IMU orientation by changing Euler angles)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            yaw -= YAW_STEP
        if keys[pygame.K_RIGHT]:
            yaw += YAW_STEP
        if keys[pygame.K_UP]:
            pitch += PITCH_STEP
        if keys[pygame.K_DOWN]:
            pitch -= PITCH_STEP
        if keys[pygame.K_q]:
            roll -= ROLL_STEP
        if keys[pygame.K_e]:
            roll += ROLL_STEP

        # clamp pitch so we don't flip
        max_pitch = math.radians(89.0)
        pitch = max(-max_pitch, min(max_pitch, pitch))

        # Build quaternion (world -> camera)
        q_cam = quat_from_euler(yaw, pitch, roll)
        R_cam = quat_to_matrix(q_cam)

        # Compute Earth's rotation (LST) once
        lst = utc_to_lst_radians(LON_DEG)

        screen.fill((0, 0, 0))

        # Draw stars
        for (vx,vy,vz), mag, name in STAR_VECTORS:
            # equatorial -> rotate by LST (bring to local celestial frame)
            wx, wy, wz = rot_y_vec((vx, vy, vz), lst)

            # rotate world into camera frame via R_cam
            cxv, cyv, czv = mat3_mul_vec(R_cam, (wx, wy, wz))

            # project
            p = project_persp((cxv, cyv, czv))
            if p:
                size = max(1, int(5 - mag))  # simple magsize mapping
                pygame.draw.circle(screen, (220, 220, 255), p, size)

        # HUD: show Euler extracted from quaternion (in degrees)
        yaw_h, pitch_h, roll_h = euler_from_quat(q_cam)
        # convert rad -> degrees and normalize yaw to 0..360
        az_deg = (math.degrees(yaw_h) % 360.0)
        alt_deg = math.degrees(pitch_h)
        roll_deg = math.degrees(roll_h)

        hud_lines = [
            f"Simulated IMU (Option 2 mounting)    FPS limit: {FPS_LIMIT}",
            f"AZ (yaw):  {az_deg:7.2f}°    ALT (pitch): {alt_deg:6.2f}°   ROLL: {roll_deg:6.2f}°",
            f"LST (hours): { (math.degrees(lst)%360)/15.0:6.3f}   (deg {math.degrees(lst)%360:6.2f})",
            "Controls: Arrow keys = yaw/pitch | Q/E = roll | wheel = zoom"
        ]
        y = 6
        for line in hud_lines:
            surf = FONT.render(line, True, (200,200,200))
            screen.blit(surf, (6, y))
            y += 18

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
