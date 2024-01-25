import math
import random

import pygame

from scripts.utils import Vec2


def get_diamond_polygon_points(pos, angle, speed, offset=Vec2((0, 0))):
    return ((pos.x + math.cos(angle) * speed * 3 - offset.x,
             pos.y + math.sin(angle) * speed * 3 - offset.y),
            (pos.x + math.cos(angle + math.pi * 0.5) * speed * 0.5 - offset.x,
             pos.y + math.sin(angle + math.pi * 0.5) * speed * 0.5 - offset.y),
            (pos.x + math.cos(angle + math.pi) * speed * 3 - offset.x,
             pos.y + math.sin(angle + math.pi) * speed * 3 - offset.y),
            (pos.x + math.cos(angle - math.pi) * speed * 0.5 - offset.x,
             pos.y + math.sin(angle - math.pi) * speed * 0.5 - offset.y))


class Spark:
    def __init__(self, pos=Vec2((0, 0)), angle=0, speed=0):
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
        points = get_diamond_polygon_points(
            self.pos, self.angle, self.speed, offset)
        pygame.draw.polygon(surf, (255, 255, 255), points)


class SparkFactory:
    @staticmethod
    def burst(pos=Vec2((0, 0))):
        sparks = []
        for _ in range(30):
            angle = random.random() * math.pi * 2  # 360 degrees
            sparks.append(Spark(pos, angle, 2 + random.random()))
        return tuple(sparks)

    @staticmethod
    def line(pos=Vec2((0, 0)), angle=0):
        return Spark(pos, angle, 5 + random.random())

    @staticmethod
    def cone(pos=Vec2((0, 0)), angle=0):
        sparks = []
        for _ in range(4):
            sparks.append(Spark(pos, random.random() - 0.5 + angle, 2 + random.random()))
        return tuple(sparks)
