import math
import random
import sys

import pygame

from scripts.assets import AssetAnim, AssetLayer, Assets, AssetTile
from scripts.clouds import Clouds
from scripts.entities import Player
from scripts.particle import Particle
from scripts.tilemap import Tilemap
from scripts.utils import Key
from scripts.vector2 import Vector2

# The number decides how often something spawns.
# >number = less spawns
SPAWN_RATE = 40_960


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('python')
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.binds = (
            Key((pygame.K_a, pygame.K_LEFT),
                lambda: self._set_movement(0, True),
                lambda: self._set_movement(0, False)),
            Key((pygame.K_d, pygame.K_RIGHT),
                lambda: self._set_movement(1, True),
                lambda: self._set_movement(1, False)),
            Key((pygame.K_SPACE, pygame.K_UP),
                lambda: self.player.jump()))

        self.assets = Assets()
        self.clouds = Clouds(self.assets.get_layers(AssetLayer.CLOUD), count=16)
        self.player = Player(self, Vector2((50, 50)), (8, 15))
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.particles = []
        self.spawns = []
        for tree in self.tilemap.extract(
                [(AssetTile.LARGE_DECOR, 2)], keep=True):
            self.spawns.append(
                pygame.Rect(*tree.pos.add((4, 4)), 23, 13))

        self.scroll = [0, 0]
        self.render_scroll = [0, 0]

    def run(self):
        while True:
            # Order is important here!
            self._clear()
            self._handle_scroll()
            self._handle_clouds()
            self._handle_tilemap()
            self._handle_player()
            self._handle_spawns()
            self._handle_particles()
            self._handle_events()
            # self.__dev()
            self._handle_screen()

    def _clear(self):
        self.display.blit(self.assets.get_layers(
            AssetLayer.BACKGROUND, 0), (0, 0))

    def _handle_scroll(self):
        self.scroll[0] += (self.player.rect().centerx -
                           self.display.get_width() / 2 -
                           self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery -
                           self.display.get_height() / 2 -
                           self.scroll[1]) / 30
        self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

    def _handle_clouds(self):
        self.clouds.update()
        self.clouds.render(self.display, offset=self.render_scroll)

    def _handle_tilemap(self):
        self.tilemap.render(self.display, offset=self.render_scroll)

    def _handle_player(self):
        self.player.update(self.tilemap,
                           (self.movement[1] - self.movement[0],
                            0))
        self.player.render(self.display, offset=self.render_scroll)

    def _handle_spawns(self):
        for rect in self.spawns:
            if random.random() * SPAWN_RATE < rect.width * rect.height:
                pos = (Vector2((rect.x, rect.y))
                       .add((random.random() * rect.width,
                             random.random() * rect.height)))
                self.particles.append(
                    Particle(self,
                             AssetAnim.PARTICLE_LEAF,
                             pos,
                             velocity=[-0.1, 0.3]))

    def _handle_particles(self):
        for particle in self.particles.copy():
            kill = particle.update()
            if particle.asset == AssetAnim.PARTICLE_LEAF:
                # Makes the leaf float left and right over time.
                # 0.035 reduces the speed of the sine curve loop.
                # 0.3 reduces the amplitude of the sine curve.
                particle.pos.x += (math.sin(particle.animation.frame * 0.035) *
                                   0.3)
            particle.render(self.display, offset=self.render_scroll)
            if kill:
                self.particles.remove(particle)

    def _handle_events(self):
        for event in pygame.event.get():
            self._handle_window(event)
            for bind in self.binds:
                bind.check(event)

    def _handle_window(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def _set_movement(self, index, bool):
        self.movement[index] = bool

    def __dev(self):
        for rect in self.spawns:
            adjusted_rect = pygame.Rect(rect.x - self.render_scroll[0],
                                        rect.y - self.render_scroll[1],
                                        rect.width,
                                        rect.height)
            pygame.draw.rect(self.display, (255, 0, 0), adjusted_rect, 1)

    def _handle_screen(self):
        self.screen.blit(
            pygame.transform.scale(self.display, self.screen.get_size()),
            (0, 0))
        pygame.display.update()
        self.clock.tick(60)


Game().run()
