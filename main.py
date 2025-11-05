import sys
import pygame
import math

import config
import tracker
import input_handler
import ui
import star_catalog
import sample_draw_utilities

def main():
    """Main function to initialize and run telescope simulation."""
    if sys.implementation.name == 'micropython':
        return  # Running on MicroPython hardware, do nothing

    pygame.init()
    screen = pygame.display.set_mode((config.W, config.H))
    pygame.display.set_caption("Telescope Tracker Emulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    # Initialize components
    camera = tracker.Camera(config.FOV_DEG, config.W, config.H)
    input_handler_instance = input_handler.InputHandler()
    ui_renderer = ui.UI(screen, font)

    # Load catalog data
    print("Loading star catalog data...")
    try:
        # Load bright stars
        bright_stars = star_catalog.load_bright_stars()
        stars_cartesian = star_catalog.get_stars_as_cartesian(bright_stars)
        print(f"Loaded {len(stars_cartesian)} bright stars")
        
        # Load constellations
        constellations = star_catalog.load_constellations()
        constellations_cartesian = star_catalog.get_constellation_lines_as_cartesian(constellations)
        print(f"Loaded {len(constellations_cartesian)} constellations")
        
        # Load Messier objects
        messiers = star_catalog.load_messier_objects()
        messiers_cartesian = star_catalog.get_messier_objects_as_cartesian(messiers)
        print(f"Loaded {len(messiers_cartesian)} Messier objects")
        
    except Exception as e:
        print(f"Error loading catalog data: {e}")
        print("Falling back to random stars...")
        # Fallback to random stars if catalog loading fails
        import starfield
        num_stars = config.NUM_STARS
        stars_cartesian = [(x, y, z, 1.0, None) for x, y, z in starfield.random_sphere_points(num_stars)]
        constellations_cartesian = []
        messiers_cartesian = []

    # Pre-generate gridlines
    longitudes = [tracker.build_longitude_line(lon) for lon in range(0, 360, config.GRID_EVERY_DEG)]
    latitudes  = [tracker.build_latitude_line(lat) for lat in range(-90, 90 + 1, config.GRID_EVERY_DEG)]

    # Print controls
    print("\nControls:")
    print("Arrow keys/WASD: Rotate camera")
    print("+/-: Zoom in/out")
    print("Z: Toggle stars")
    print("Shift+Z: Toggle star names")
    print("C: Toggle constellations")
    print("Shift+C: Toggle constellation names")
    print("M: Toggle Messier objects")
    print("Shift+M: Toggle Messier names")
    print("ESC: Quit")

    running = True
    while running:
        # Calculate delta time
        dt = clock.tick(config.FPS) / 1000.0

        # Process input
        input_handler_instance.process_input(camera, dt)
        if input_handler_instance.should_quit():
            running = False

        # Get toggle states
        toggle_states = input_handler_instance.get_toggle_states()

        # Clear screen
        screen.fill(config.BACKGROUND)

        # Draw gridlines
        tracker.draw_grid(screen, camera, longitudes, config.GRID_COLOR)
        tracker.draw_grid(screen, camera, latitudes, config.GRID_COLOR)

        # Draw catalog objects based on toggle states
        # Draw constellation lines first (so they appear behind stars)
        if toggle_states['show_constellations'] and constellations_cartesian:
            sample_draw_utilities.draw_constellations_from_cartesian(
                screen, constellations_cartesian, camera, color=(100, 100, 255),
                show_names=toggle_states['show_constellation_names'], font=font
            )
        
        # Draw stars
        if toggle_states['show_stars'] and stars_cartesian:
            sample_draw_utilities.draw_stars_from_cartesian(
                screen, stars_cartesian, camera, color=config.STAR_COLOR,
                show_names=toggle_states['show_star_names'], font=font
            )
        
        # Draw Messier objects
        if toggle_states['show_messiers'] and messiers_cartesian:
            sample_draw_utilities.draw_messiers_from_cartesian(
                screen, messiers_cartesian, camera, color=(255, 180, 80),
                show_names=toggle_states['show_messier_names'], font=font
            )

        # Draw UI elements
        ui_renderer.draw_crosshair()
        ui_renderer.draw_hud(camera)

        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
