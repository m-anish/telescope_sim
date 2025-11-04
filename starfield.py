"""Starfield generator and renderer."""
import random
import pygame


class StarField:
    def __init__(self, width, height, count=200):
        self.width = width
        self.height = height
        self.stars = []
        for _ in range(count):
            x = random.randrange(0, width)
            y = random.randrange(0, height)
            z = random.uniform(0.2, 1.0)  # brightness/size factor
            self.stars.append((x, y, z))

    def draw(self, surface):
        for x, y, z in self.stars:
            size = max(1, int(2 * z))
            color = (int(200 * z + 55),) * 3
            pygame.draw.circle(surface, color, (int(x), int(y)), size)
