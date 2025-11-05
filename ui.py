import pygame
import config

class UI:
    """Handles rendering of UI elements like HUD and status messages."""
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw_hud(self, camera):
        """Draws the Heads-Up Display with telemetry information."""
        hud_lines = [
            f"Yaw: {camera.yaw:.1f}°  Pitch: {camera.pitch:.1f}°  FOV: {camera.fov:.1f}°",
            "Arrows: look around   +/-: zoom   Esc: quit"
        ]
        y_pos = 8
        for line in hud_lines:
            text_surface = self.font.render(line, True, config.TEXT_COLOR)
            self.screen.blit(text_surface, (8, y_pos))
            y_pos += 20

    def draw_crosshair(self):
        """Draws a simple crosshair at the center of the screen."""
        cx, cy = config.W // 2, config.H // 2
        crosshair_color = (80, 80, 120)
        pygame.draw.line(self.screen, crosshair_color, (cx - 8, cy), (cx + 8, cy), 1)
        pygame.draw.line(self.screen, crosshair_color, (cx, cy - 8), (cx, cy + 8), 1)
