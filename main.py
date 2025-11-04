"""Simple PyGame skeleton for telescope_sim.
Runs a window, draws a starfield and a moving tracker target.
"""
import sys
import pygame
from ui import draw_fps
from starfield import StarField
from tracker import Tracker


WIDTH, HEIGHT = 800, 600


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Telescope Simulator")
    clock = pygame.time.Clock()

    stars = StarField(WIDTH, HEIGHT, count=200)
    tracker = Tracker(WIDTH // 2, HEIGHT // 2)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                tracker.set_target(event.pos)

        tracker.update(dt)

        screen.fill((0, 0, 10))
        stars.draw(screen)
        tracker.draw(screen)
        draw_fps(screen, clock)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
