import pygame, math, random, sys

pygame.init()
WIDTH, HEIGHT = 320, 240
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Telescope Tracker Emulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 16)

# --- Simulation parameters ---
az, alt = 0, 45       # telescope pointing (degrees)
target_az, target_alt = 90, 60  # target object
stars = [(random.uniform(0,360), random.uniform(0,90), random.randint(1,3)) for _ in range(200)]

def sky_to_screen(star_az, star_alt, view_az, view_alt):
    """Convert sky coordinates to screen position (approximate)"""
    daz = (star_az - view_az + 540) % 360 - 180
    dalt = star_alt - view_alt
    x = WIDTH/2 + daz * 2     # 2 px per degree horizontally
    y = HEIGHT/2 - dalt * 3   # 3 px per degree vertically
    return int(x), int(y)

def draw_starfield():
    screen.fill((0,0,0))
    for saz, salt, size in stars:
        x, y = sky_to_screen(saz, salt, az, alt)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            pygame.draw.circle(screen, (255,0,0), (x,y), size)

def draw_arrow():
    # compute direction arrow toward target
    daz = (target_az - az + 540) % 360 - 180
    dalt = target_alt - alt
    length = min(60, math.hypot(daz, dalt)*2)
    angle = math.atan2(-dalt, daz)
    cx, cy = WIDTH//2, HEIGHT//2
    x2 = cx + length*math.cos(angle)
    y2 = cy + length*math.sin(angle)
    pygame.draw.line(screen, (255,0,0), (cx, cy), (x2, y2), 2)
    pygame.draw.polygon(screen, (255,0,0),
        [(x2, y2),
         (x2 - 6*math.cos(angle - 0.4), y2 - 6*math.sin(angle - 0.4)),
         (x2 - 6*math.cos(angle + 0.4), y2 - 6*math.sin(angle + 0.4))])

def draw_ui():
    txt = f"AZ:{az:5.1f}  ALT:{alt:5.1f}"
    lbl = font.render(txt, True, (255,0,0))
    screen.blit(lbl, (5, 5))
    txt2 = f"Target→ AZ:{target_az}, ALT:{target_alt}"
    lbl2 = font.render(txt2, True, (255,0,0))
    screen.blit(lbl2, (5, 22))

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  az -= 1
    if keys[pygame.K_RIGHT]: az += 1
    if keys[pygame.K_UP]:    alt += 1
    if keys[pygame.K_DOWN]:  alt -= 1
    alt = max(0, min(90, alt))   # clamp altitude

    draw_starfield()
    draw_arrow()
    draw_ui()
    pygame.display.flip()
    clock.tick(30)
