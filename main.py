import pygame, math, random, sys

pygame.init()
WIDTH, HEIGHT = 320, 240
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Telescope Tracker Emulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 16)

# --- Telescope state ---
az, alt = 0, 45
target_az, target_alt = 90, 60
mode = "menu"
selected_idx = 0
object_list = [
    ("Vega", 80, 60),
    ("Betelgeuse", 85, 25),
    ("Sirius", 120, 20),
    ("Polaris", 0, 89),
    ("M42 Orion Nebula", 83, 25),
]

# --- Generate background stars ---
stars = [(random.uniform(0,360), random.uniform(0,90), random.randint(1,3))
         for _ in range(200)]

# ---------------- Functions ----------------

def sky_to_screen(star_az, star_alt, view_az, view_alt):
    """Convert sky coordinates to screen coordinates."""
    daz = (star_az - view_az + 540) % 360 - 180
    dalt = star_alt - view_alt
    x = WIDTH/2 + daz * 2
    y = HEIGHT/2 - dalt * 3
    return int(x), int(y)

def draw_starfield():
    screen.fill((0,0,0))
    for saz, salt, size in stars:
        x, y = sky_to_screen(saz, salt, az, alt)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            pygame.draw.circle(screen, (255,0,0), (x,y), size)

def draw_arrow():
    """Draw an arrow toward target direction."""
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

def draw_menu():
    screen.fill((0,0,0))
    items = ["Align", "Select Object", "Track", "Exit"]
    for i, name in enumerate(items):
        color = (255,0,0) if i == selected_idx else (120,0,0)
        lbl = font.render(name, True, color)
        screen.blit(lbl, (100, 60 + i*25))

def draw_ui():
    # --- Top HUD ---
    txt = f"AZ:{az:5.1f}  ALT:{alt:5.1f}"
    lbl = font.render(txt, True, (255,0,0))
    screen.blit(lbl, (5, 5))
    txt2 = f"Target→ AZ:{target_az}, ALT:{target_alt}"
    lbl2 = font.render(txt2, True, (255,0,0))
    screen.blit(lbl2, (5, 22))

    # --- Bottom status line ---
    status_text = ""
    if mode == "align":
        status_text = "Align mode: Adjust to known star"
    elif mode == "select":
        name, _, _ = object_list[selected_idx]
        status_text = f"Select object: {name}"
    elif mode == "track":
        status_text = "Tracking active"
    elif mode == "menu":
        status_text = "Press ENTER to select, ESC to exit"

    if status_text:
        lbl3 = font.render(status_text, True, (255,0,0))
        text_rect = lbl3.get_rect()
        text_rect.midbottom = (WIDTH // 2, HEIGHT - 4)
        screen.blit(lbl3, text_rect)

# ---------------- Main Loop ----------------

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if e.type == pygame.KEYDOWN:
            # --- Menu navigation ---
            if mode == "menu":
                if e.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % 4
                elif e.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % 4
                elif e.key == pygame.K_RETURN:
                    if selected_idx == 0: mode = "align"
                    elif selected_idx == 1: mode = "select"
                    elif selected_idx == 2: mode = "track"
                    elif selected_idx == 3: pygame.quit(); sys.exit()
            else:
                if e.key == pygame.K_ESCAPE:
                    mode = "menu"

            # --- Object selection ---
            if mode == "select":
                if e.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(object_list)
                elif e.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(object_list)
                elif e.key == pygame.K_RETURN:
                    name, target_az, target_alt = object_list[selected_idx]
                    mode = "track"

    keys = pygame.key.get_pressed()

    # --- Telescope movement (in all non-menu modes) ---
    if mode in ["align", "track"]:
        if keys[pygame.K_LEFT]:  az -= 1
        if keys[pygame.K_RIGHT]: az += 1
        if keys[pygame.K_UP]:    alt += 1
        if keys[pygame.K_DOWN]:  alt -= 1
        alt = max(0, min(90, alt))

    # --- Draw current mode ---
    if mode == "menu":
        draw_menu()
    else:
        draw_starfield()
        if mode in ["align", "track"]:
            draw_arrow()
        draw_ui()

    pygame.display.flip()
    clock.tick(30)
