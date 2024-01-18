import math
import random
import sys

import pygame

from app import App
from scripts.assets import AssetAnim, AssetLayer, AssetTile
from scripts.clouds import Clouds
from scripts.entities import Player
from scripts.particle import Particle
from scripts.utils import Key, Vector2

# The number decides how often something spawns.
# >number = less spawns
SPAWN_RATE = 40_960


class Game(App):
    def __init__(self):
        super().__init__(title='python',
                         map_path='map.json',
                         res_base=(320, 180),
                         res_scale=2.0)

        self.binds = (
            Key((pygame.K_a, pygame.K_LEFT),
                lambda: self.direction.toggle_left(),
                lambda: self.direction.toggle_left()),
            Key((pygame.K_d, pygame.K_RIGHT),
                lambda: self.direction.toggle_right(),
                lambda: self.direction.toggle_right()),
            Key((pygame.K_SPACE, pygame.K_UP),
                lambda: self.player.jump()))

        self.clouds = Clouds(self.assets.get_layers(AssetLayer.CLOUD), count=16)
        self.player = Player(self, (8, 15), Vector2((50, 50)))

        self.particles = []
        self.spawns = []
        for tree in self.tilemap.extract([(AssetTile.LARGE_DECOR, 2)],
                                         keep=True):
            self.spawns.append(
                pygame.Rect(*tree.pos.add((4, 4)), 23, 13))

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
            self._render()

    def _clear(self):
        self.display.blit(self.assets.get_layers(AssetLayer.BACKGROUND, 0),
                          (0, 0))

    def _handle_scroll(self):
        self.scroll = self.scroll.add(((self.player.rect().centerx
                                       - self.display.get_width() / 2
                                       - self.scroll.x) / 30,
                                       (self.player.rect().centery
                                       - self.display.get_height() / 2
                                       - self.scroll.y) / 30))
        self.render_scroll = self.scroll.int()

    def _handle_clouds(self):
        self.clouds.update()
        self.clouds.render(self.display, offset=self.render_scroll)

    def _handle_tilemap(self):
        self.tilemap.render(self.display, offset=self.render_scroll)

    def _handle_player(self):
        self.player.update(self.tilemap,
                           (self.direction.right - self.direction.left,
                            self.direction.down - self.direction.up))
        self.player.render(self.display, offset=self.render_scroll)

    def _handle_spawns(self):
        for rect in self.spawns:
            if random.random() * SPAWN_RATE < rect.width * rect.height:
                self.particles.append(
                    Particle(self,
                             AssetAnim.PARTICLE_LEAF,
                             Vector2((rect.x, rect.y))
                             .add((random.random() * rect.width,
                                  random.random() * rect.height)),
                             velocity=(-0.1, 0.3),
                             random_frame=True))

    def _handle_particles(self):
        for particle in self.particles.copy():
            kill = particle.update()
            if particle.asset == AssetAnim.PARTICLE_LEAF:
                # Makes the leaf float left and right over time.
                # 0.035 reduces the speed of the sine curve loop.
                # 0.3 reduces the amplitude of the sine curve.
                particle.pos.add(
                    (math.sin(particle.animation.frame * 0.035) * 0.3, 0))
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

    def __dev(self):
        for rect in self.spawns:
            adjusted_rect = pygame.Rect(*Vector2((rect.x, rect.y))
                                        .sub(self.render_scroll),
                                        *rect.size)
            pygame.draw.rect(self.display, (255, 0, 0), adjusted_rect, 1)


Game().run()
