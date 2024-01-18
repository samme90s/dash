from abc import ABC, abstractmethod

import pygame

from scripts.assets import Assets
from scripts.tilemap import Tilemap
from scripts.utils import Direction, Vector2


class App(ABC):
    def __init__(self, title: str,
                 map_path: str,
                 res_base: tuple = (320, 180),
                 res_scale: float = 2.0):
        self.RES_SCALE = res_scale
        pygame.init()
        pygame.display.set_caption(title)
        self.display = pygame.Surface(res_base)
        self.screen = pygame.display.set_mode((res_base[0] * res_scale,
                                               res_base[1] * res_scale))
        self.clock = pygame.time.Clock()

        self.direction = Direction()
        self.assets = Assets()
        self.tilemap = Tilemap(self, tile_size=16)
        try:
            self.tilemap.load(map_path)
        except FileNotFoundError:
            raise FileNotFoundError

        self.scroll = Vector2((0, 0))
        self.render_scroll = Vector2((0, 0))

    @abstractmethod
    def run(self):
        raise NotImplementedError
