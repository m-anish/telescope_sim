import pygame
import math
import datetime
import time
import sys
import csv

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Digital Finderscope Simulator")
clock = pygame.time.Clock()

CX, CY = WIDTH // 2, HEIGHT // 2

# Adjustable FOV via focal length (bigger = more zoom)
focal = 600

# Initial simulated IMU orientation (look East, alt=0)
cam_alt = 0.0                        # radians, pitch
cam_az = math.radians(90.0)          # radians, yaw

# How fast arrow keys move camera (simulated IMU output)
ALT_STEP = math.radians(1.0)
AZ_STEP = math.radians(1.0)

FONT = pygame.font.SysFont("Arial", 18)

# ---- Load star catalog (HYG database, 4.0 mag cutoff) ----
BRIGHT_STARS = []
with open('./data/hyg_stars_4_0mag.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        ra = float(row['RA_deg'])
        dec = float(row['Dec_deg'])
        mag = float(row['Magnitude'])
        name = row['Name'].strip() if row['Name'] else None
        BRIGHT_STARS.append((ra, dec, mag, name))


# Observer (Dharamsala)
LAT_DEG = 32.24
LON_DEG = 76.32
LAT = math.radians(LAT_DEG)

# ---- Time to LST (sidereal time) ----
def utc_to_lst():
    dt = datetime.datetime.utcnow()
    # Julian date
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    JDN = dt.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
    JD = JDN + (dt.hour - 12)/24 + dt.minute/1440 + dt.second/86400
    T = (JD - 2451545.0) / 36525.0
    GMST = 280.46061837 + 360.98564736629*(JD-2451545) + 0.000387933*T*T - T*T*T/38710000.0
    GMST = math.radians(GMST % 360)
    LST = (GMST + math.radians(LON_DEG)) % (2*math.pi)
    return LST

# ---- Convert RA/Dec to fixed unit vector (equatorial) ----
def radec_to_vector(ra_deg, dec_deg):
    ra = math.radians(ra_deg)
    dec = math.radians(dec_deg)
    x = math.cos(dec) * math.cos(ra)
    y = math.cos(dec) * math.sin(ra)
    z = math.sin(dec)
    return (x, y, z)

STAR_VECTORS = [(radec_to_vector(*star[:2]), star[2], star[3]) for star in BRIGHT_STARS]

# ---- Rotate around Y (Earth rotation adjusts RA->local sky) ----
def rot_y(v, a):
    x, y, z = v
    ca = math.cos(a); sa = math.sin(a)
    return (ca*x + sa*z, y, -sa*x + ca*z)

# ---- Camera pitch rotation (X axis) ----
def rot_x(v, a):
    x, y, z = v
    ca = math.cos(a); sa = math.sin(a)
    return (x, ca*y - sa*z, sa*y + ca*z)

# ---- Project to screen ----
def project(v):
    x,y,z = v
    if z <= 0: return None
    sx = CX + focal * (x / z)
    sy = CY - focal * (y / z)
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        return (int(sx), int(sy))
    return None

# -------------------- Main Loop --------------------
while True:
    dt = clock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            focal *= 1.1 if event.y > 0 else 1/1.1

    # Simulated IMU orientation using arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  cam_az -= AZ_STEP
    if keys[pygame.K_RIGHT]: cam_az += AZ_STEP
    if keys[pygame.K_UP]:    cam_alt += ALT_STEP
    if keys[pygame.K_DOWN]:  cam_alt -= ALT_STEP

    # Clamp pitch
    cam_alt = max(-math.radians(85), min(math.radians(85), cam_alt))

    # Compute Earth rotation (sky position) once per frame
    lst = utc_to_lst()

    screen.fill((0, 0, 0))

    # Draw stars
    for (vx,vy,vz), mag, name in STAR_VECTORS:
        # Earth rotation = shift RA → local sky
        wx, wy, wz = rot_y((vx,vy,vz), lst)

        # Camera orientation
        rx, ry, rz = rot_y((wx,wy,wz), -cam_az)
        rx, ry, rz = rot_x((rx,ry,rz), cam_alt)

        p = project((rx,ry,rz))
        if p:
            size = max(1, int(5 - mag))
            pygame.draw.circle(screen, (220, 220, 255), p, size)
            if name and mag <= 4:
                label = FONT.render(name, True, (200, 200, 200))
                screen.blit(label, (p[0] + 5, p[1] - 5))

    # HUD
    hud = FONT.render(
        f"ALT: {math.degrees(cam_alt):.1f}°    AZ: {math.degrees(cam_az)%360:.1f}°",
        True, (200,200,200)
    )
    screen.blit(hud, (10,10))

    pygame.display.flip()
