"""UI utilities: simple menu text and FPS display."""
import pygame


def draw_fps(surface, clock, pos=(10, 10), color=(200, 200, 200)):
    """Draw frames-per-second in the top-left corner."""
    font = pygame.font.Font(None, 24)
    fps = clock.get_fps()
    text = font.render(f"FPS: {fps:.0f}", True, color)
    surface.blit(text, pos)
