import random
from abc import ABC, abstractmethod

import pygame

from scripts.assets import Assets
from scripts.tilemap import Tilemap
from scripts.utils import Dir, Vec2

SILHOUETTE_OFFSETS = ((-1, 0), (1, 0), (0, -1), (0, 1))


class Instance(ABC):
    def __init__(self,
                 title: str,
                 res_base: tuple = (320, 180),
                 res_scale: float = 2.0):
        self.RES_SCALE = res_scale
        pygame.init()
        pygame.display.set_caption(title)
        # "SRCALPHA" indicates the surface contains an alpha channel.
        self.fore_d = pygame.Surface(res_base, pygame.SRCALPHA)
        self.back_d = pygame.Surface(res_base)
        self.screen = pygame.display.set_mode((res_base[0] * res_scale,
                                               res_base[1] * res_scale))
        self.clock = pygame.time.Clock()
        # Update this value every frame.
        self.delta_time = 60 / 1000

        self.dir = Dir()
        self.assets = Assets()
        self.tilemap = Tilemap(self, size=16)
        self.shake = 0
        self.scroll = Vec2((0, 0))
        self.render_scroll = Vec2((0, 0))

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def _load_level(self, map_id):
        try:
            self.tilemap.load(f'data/maps/{map_id}.json')
        except FileNotFoundError:
            raise FileNotFoundError

    def _clear(self):
        self.fore_d.fill((0, 0, 0, 0))
        self.back_d.fill((0, 0, 0))

    def _render(self):
        display_mask = pygame.mask.from_surface(self.fore_d)
        display_silhouette = display_mask.to_surface(
            setcolor=(0, 0, 0, 180),
            unsetcolor=(0, 0, 0, 0))
        # Creates the outline by offsetting the silhouette.
        for offset in SILHOUETTE_OFFSETS:
            self.back_d.blit(display_silhouette, offset)

        # Apply the foreground display to the background before rendering the
        # background.
        self.back_d.blit(self.fore_d, (0, 0))
        self.screen.blit(
            pygame.transform.scale(self.back_d, self.screen.get_size()),
            self.__get_offset())
        pygame.display.update()
        self.delta_time = self.clock.tick(60) / 1000

    def __get_offset(self):
        # Normalize screenshake.
        self.shake = max(0, self.shake - 1)
        return (random.random() * self.shake - self.shake / 2,
                random.random() * self.shake - self.shake / 2)
