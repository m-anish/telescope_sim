import pygame
import math

import config
import starfield
import tracker
import input_handler
import ui

def main():
    """Main function to initialize and run the telescope simulation."""
    pygame.init()
    screen = pygame.display.set_mode((config.W, config.H))
    pygame.display.set_caption("Telescope Tracker Emulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    # Initialize components
    camera = tracker.Camera(config.FOV_DEG, config.W, config.H)
    input_handler_instance = input_handler.InputHandler()
    ui_renderer = ui.UI(screen, font)

    # Generate stars and their sizes
    num_stars = config.NUM_STARS
    stars = starfield.random_sphere_points(num_stars)
    star_sizes = starfield.generate_star_sizes(num_stars)

    # Pre-generate gridlines
    longitudes = [tracker.build_longitude_line(lon) for lon in range(0, 360, config.GRID_EVERY_DEG)]
    latitudes  = [tracker.build_latitude_line(lat) for lat in range(-90, 90 + 1, config.GRID_EVERY_DEG)]

    running = True
    while running:
        # Calculate delta time
        dt = clock.tick(config.FPS) / 1000.0

        # Process input
        input_handler_instance.process_input(camera, dt)
        if input_handler_instance.should_quit():
            running = False

        # Clear screen
        screen.fill(config.BACKGROUND)

        # Draw gridlines
        tracker.draw_grid(screen, camera, longitudes, config.GRID_COLOR)
        tracker.draw_grid(screen, camera, latitudes, config.GRID_COLOR)

        # Draw stars
        for i, v in enumerate(stars):
            vc = camera.world_to_camera(v)
            p = camera.project(vc)
            if not p: continue
            sx, sy, z = p
            r = star_sizes[i]
            pygame.draw.circle(screen, config.STAR_COLOR, (int(sx), int(sy)), r)

        # Draw UI elements
        ui_renderer.draw_crosshair()
        ui_renderer.draw_hud(camera)

        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
