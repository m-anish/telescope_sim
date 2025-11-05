import pygame
import config
from tracker import clamp # Import clamp from tracker.py

class InputHandler:
    """Handles all user input for the application."""
    def __init__(self):
        self.quit_requested = False
        # Toggle states for catalog objects
        self.show_stars = True
        self.show_constellations = True
        self.show_messiers = True
        self.show_ephemeris = True
        # Toggle states for name display
        self.show_star_names = False
        self.show_messier_names = False
        self.show_constellation_names = False
        self.show_ephemeris_names = False

    def process_input(self, camera, dt):
        """
        Processes Pygame events and keyboard input to update camera state.
        
        Args:
            camera (Camera): The camera object to control.
            dt (float): Time delta since the last frame, used for smooth movement.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_requested = True # Or handle mode switching later
                elif event.key == pygame.K_z:
                    # Check if shift is pressed for uppercase
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        self.show_star_names = not self.show_star_names
                        print(f"Star names: {'ON' if self.show_star_names else 'OFF'}")
                    else:
                        self.show_stars = not self.show_stars
                        print(f"Stars: {'ON' if self.show_stars else 'OFF'}")
                elif event.key == pygame.K_c:
                    # Check if shift is pressed for uppercase
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        self.show_constellation_names = not self.show_constellation_names
                        print(f"Constellation names: {'ON' if self.show_constellation_names else 'OFF'}")
                    else:
                        self.show_constellations = not self.show_constellations
                        print(f"Constellations: {'ON' if self.show_constellations else 'OFF'}")
                elif event.key == pygame.K_m:
                    # Check if shift is pressed for uppercase
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        self.show_messier_names = not self.show_messier_names
                        print(f"Messier names: {'ON' if self.show_messier_names else 'OFF'}")
                    else:
                        self.show_messiers = not self.show_messiers
                        print(f"Messier objects: {'ON' if self.show_messiers else 'OFF'}")
                elif event.key == pygame.K_p:
                    # Check if shift is pressed for uppercase
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        self.show_ephemeris_names = not self.show_ephemeris_names
                        print(f"Ephemeris names: {'ON' if self.show_ephemeris_names else 'OFF'}")
                    else:
                        self.show_ephemeris = not self.show_ephemeris
                        print(f"Ephemeris objects: {'ON' if self.show_ephemeris else 'OFF'}")

        keys = pygame.key.get_pressed()

        # Direct rotation
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            camera.yaw -= config.YAW_SPEED_DEG * dt # Decrease yaw for left movement (left-to-right pan)
            # Normalize yaw to be within [0, 360) degrees
            camera.yaw = (camera.yaw % 360 + 360) % 360
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            camera.yaw += config.YAW_SPEED_DEG * dt # Increase yaw for right movement (right-to-left pan)
            # Normalize yaw to be within [0, 360) degrees
            camera.yaw = (camera.yaw % 360 + 360) % 360
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            camera.pitch += config.PITCH_SPEED_DEG * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            camera.pitch -= config.PITCH_SPEED_DEG * dt
        
        # Clamp pitch to avoid flipping
        camera.pitch = clamp(camera.pitch, -90.0, 90.0)

        # Zoom
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            camera.fov -= config.ZOOM_SPEED * dt
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
            camera.fov += config.ZOOM_SPEED * dt
        
        # Clamp FOV
        camera.fov = clamp(camera.fov, config.FOV_MIN, config.FOV_MAX)
        camera.update_focal()

    def should_quit(self):
        """Returns True if the user has requested to quit."""
        return self.quit_requested

    def get_toggle_states(self):
        """Returns the current toggle states for catalog objects."""
        return {
            'show_stars': self.show_stars,
            'show_constellations': self.show_constellations,
            'show_messiers': self.show_messiers,
            'show_ephemeris': self.show_ephemeris,
            'show_star_names': self.show_star_names,
            'show_messier_names': self.show_messier_names,
            'show_constellation_names': self.show_constellation_names,
            'show_ephemeris_names': self.show_ephemeris_names
        }
