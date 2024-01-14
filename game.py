import sys

import pygame

from scripts.assets import AssetLayer, Assets
from scripts.clouds import Clouds
from scripts.entities import Player
from scripts.tilemap import Tilemap
from scripts.utils import Key
from scripts.vector2 import Vector2


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('python')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = Assets()

        self.clouds = Clouds(self.assets.get_layers(AssetLayer.CLOUD), count=16)

        self.player = Player(self, Vector2((50, 50)), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]
        self.render_scroll = [0, 0]

    def run(self):
        while True:
            # Order is important here!
            self.clear()
            self.handle_scroll()
            self.handle_clouds()
            self.handle_tilemap()
            self.handle_player()
            self.handle_events()
            self.handle_screen()

    def clear(self):
        self.display.blit(self.assets.get_layers(
            AssetLayer.BACKGROUND, 0), (0, 0))

    def handle_scroll(self):
        self.scroll[0] += (self.player.rect().centerx -
                           self.display.get_width() / 2 -
                           self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery -
                           self.display.get_height() / 2 -
                           self.scroll[1]) / 30
        self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

    def handle_clouds(self):
        self.clouds.update()
        self.clouds.render(self.display, offset=self.render_scroll)

    def handle_tilemap(self):
        self.tilemap.render(self.display, offset=self.render_scroll)

    def handle_player(self):
        self.player.update(self.tilemap,
                           (self.movement[1] - self.movement[0], 0))
        self.player.render(self.display, offset=self.render_scroll)

    def handle_events(self):
        for event in pygame.event.get():
            self._handle_window(event)
            self._handle_keys(event)

    def _handle_window(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def _handle_keys(self, event):
        Key((pygame.K_a, pygame.K_LEFT),
            lambda: self._set_movement(0, True),
            lambda: self._set_movement(0, False)).check(event)
        Key((pygame.K_d, pygame.K_RIGHT),
            lambda: self._set_movement(1, True),
            lambda: self._set_movement(1, False)).check(event)
        Key((pygame.K_SPACE, pygame.K_UP),
            lambda: self.player.jump()).check(event)

    def _set_movement(self, index, bool):
        self.movement[index] = bool

    def handle_screen(self):
        self.screen.blit(
            pygame.transform.scale(self.display, self.screen.get_size()),
            (0, 0))
        pygame.display.update()
        self.clock.tick(60)


Game().run()
