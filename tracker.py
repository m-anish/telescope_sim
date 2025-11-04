"""Simple tracker logic: moves a marker toward a target position."""
import math
import pygame


class Tracker:
    def __init__(self, x, y, speed=200.0):
        self.pos = pygame.math.Vector2(x, y)
        self.target = pygame.math.Vector2(x, y)
        self.speed = speed

    def set_target(self, pos):
        self.target = pygame.math.Vector2(pos)

    def update(self, dt):
        dir_vec = self.target - self.pos
        dist = dir_vec.length()
        if dist < 1e-3:
            return
        dir_vec.normalize_ip()
        move = dir_vec * self.speed * dt
        if move.length() >= dist:
            self.pos = self.target
        else:
            self.pos += move

    def draw(self, surface):
        # draw line to target and a circle at current position
        pygame.draw.line(surface, (100, 255, 100), (int(self.pos.x), int(self.pos.y)), (int(self.target.x), int(self.target.y)), 1)
        pygame.draw.circle(surface, (255, 100, 100), (int(self.pos.x), int(self.pos.y)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.target.x), int(self.target.y)), 4, 1)
