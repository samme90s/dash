import math

import pygame

from scripts.utils import Vec2


class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = pos.deepcopy()
        # Represents polar coordinates:
        self.angle = angle
        self.speed = speed

    def update(self):
        self.pos.x += math.cos(self.angle) * self.speed
        self.pos.y += math.sin(self.angle) * self.speed

        self.speed = max(0, self.speed - 0.1)
        return not self.speed

    def render(self, surf, offset=Vec2((0, 0))):
        render_points = [
            (self.pos.x + math.cos(self.angle) * self.speed * 3 - offset.x,
             self.pos.y + math.sin(self.angle) * self.speed * 3 - offset.y),
            (self.pos.x + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset.x,
             self.pos.y + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset.y),
            (self.pos.x + math.cos(self.angle + math.pi) * self.speed * 3 - offset.x,
             self.pos.y + math.sin(self.angle + math.pi) * self.speed * 3 - offset.y),
            (self.pos.x + math.cos(self.angle - math.pi) * self.speed * 0.5 - offset.x,
             self.pos.y + math.sin(self.angle - math.pi) * self.speed * 0.5 - offset.y)
        ]

        pygame.draw.polygon(surf, (255, 255, 255), render_points)
