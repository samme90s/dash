import math
import os
import random
import sys

import pygame

from instance import Instance
from scripts.assets import AssetAnim, AssetLayer, AssetSprite, AssetTile
from scripts.clouds import Clouds
from scripts.entities import Enemy, Player
from scripts.particle import Particle, ParticleSpawner
from scripts.sounds import SoundAmbience, SoundEffect, SoundMusic, Sounds
from scripts.spark import Spark
from scripts.utils import Key, Vec2, get_rects


class Game(Instance):
    def __init__(self):
        super().__init__(title='python',
                         res_base=(320, 180),
                         res_scale=3.0)

        self.binds = (
            Key((pygame.K_a, pygame.K_LEFT),
                lambda: self.dir.toggle_left(),
                lambda: self.dir.toggle_left()),
            Key((pygame.K_d, pygame.K_RIGHT),
                lambda: self.dir.toggle_right(),
                lambda: self.dir.toggle_right()),
            Key((pygame.K_SPACE, pygame.K_UP),
                lambda: self.player.jump()),
            Key(pygame.K_LSHIFT,
                lambda: self.player.dash()))

        self.sounds = Sounds()
        self.clouds = Clouds(self.assets.get_layers(AssetLayer.CLOUD), count=16)
        self.level = 0

    def run(self):
        self._load_level(self.level)
        self.sounds.load_music(SoundMusic.MUSIC, 0.5)
        self.sounds.get_ambient(SoundAmbience.AMBIENCE).play(-1)

        while True:
            # Order is important here!
            self._clear()

            if self.player.hitpoint.is_dead():
                self.transition = min(30, self.transition + 1)
                if self.transition >= 30:
                    self._load_level(self.level)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(
                        len(os.listdir('data/maps/')) - 1, self.level + 1)
                    self._load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            self._handle_scroll()
            self._handle_clouds()
            self._handle_tilemap()
            self._handle_enemies()
            self._handle_player()
            self._handle_projs()
            self._handle_sparks()
            self._handle_parts()
            self._handle_events()

            if self.transition:
                transition_surf = pygame.Surface(self.fore_d.get_size())
                pygame.draw.circle(transition_surf,
                                   (255, 255, 255),
                                   (self.fore_d.get_width() // 2,
                                    self.fore_d.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.fore_d.blit(transition_surf, (0, 0))

            self._render()

    def _load_level(self, map_id):
        super()._load_level(map_id)
        tree_rects = get_rects(
            game=self,
            type=AssetTile.LARGE_DECOR,
            var=2,
            keep=True,
            size=Vec2((23, 13)),
            offset=Vec2((4, 4)))
        self.leaf_spawner = ParticleSpawner(
            game=self,
            asset=AssetAnim.PARTICLE_LEAF,
            vel=Vec2((-0.1, 0.3)),
            rand_f=True,
            rects=tree_rects,
            spawn_r=0.016)

        self.player = Player(self, (8, 15), Vec2((0, 0)))
        self.enemies = []
        self.parts = []
        self.projs = []
        self.sparks = []
        self.transition = -30
        self._handle_spawners()

    def _handle_spawners(self):
        for spawn in self.tilemap.extract([
                (AssetTile.SPAWNERS, 0),
                (AssetTile.SPAWNERS, 1)
        ]):
            if spawn.var == 0:
                self.player.pos = spawn.pos
            else:
                self.enemies.append(Enemy(self, (8, 15), spawn.pos))

    def _clear(self):
        super()._clear()
        self.back_d.blit(
            self.assets.get_layers(AssetLayer.BACKGROUND, 0), (0, 0))

    def _handle_scroll(self):
        self.scroll = self.scroll.add(
            ((self.player.rect().centerx
              - self.fore_d.get_width() / 2
              - self.scroll.x) / 30,
             (self.player.rect().centery
              - self.fore_d.get_height() / 2
              - self.scroll.y) / 30))
        self.render_scroll = self.scroll.int()

    def _handle_clouds(self):
        self.clouds.update()
        self.clouds.render(self.back_d, offset=self.render_scroll)

    def _handle_tilemap(self):
        self.tilemap.render()

    def _handle_enemies(self):
        for enemy in self.enemies.copy():
            enemy.update(Vec2((0, 0)))
            enemy.render()

            if enemy.hitpoint.is_dead():
                self.enemies.remove(enemy)

    def _handle_player(self):
        if not self.player.hitpoint.is_dead():
            self.player.update(Vec2((self.dir.right - self.dir.left,
                                     self.dir.down - self.dir.up)))
            self.player.render()

    # [[x, y], direction, timer]
    def _handle_projs(self):
        for proj in self.projs.copy():
            proj[0].x += proj[1]
            proj[2] += 1
            img = self.assets.get_sprite(AssetSprite.PROJECTILE)
            self.fore_d.blit(
                img,
                (proj[0].x - img.get_width() / 2 - self.render_scroll.x,
                 proj[0].y - img.get_height() / 2 - self.render_scroll.y))
            if self.tilemap.solid_check(proj[0]) or proj[2] > 360:
                self.projs.remove(proj)
                for i in range(4):
                    self.sparks.append(Spark(proj[0], random.random(
                    ) - 0.5 + (math.pi if proj[1] > 0 else 0), 2 + random.random()))
            elif self.player.dashing_dur < 50:
                if self.player.rect().collidepoint(proj[0].tuple()):
                    self.projs.remove(proj)
                    self.sounds.get_sfx(SoundEffect.HIT).play()
                    self.shake = max(48, self.shake)
                    self.player.hitpoint.reduce(1)
                    for _ in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(Vec2(self.player.rect().center),
                                                 angle,
                                                 2 + random.random()))
                        self.parts.append(Particle(self,
                                                   AssetAnim.PARTICLE_DARK,
                                                   Vec2(
                                                       self.player.rect().center),
                                                   vel=Vec2((math.cos(angle + math.pi) * speed * 0.5,
                                                             math.sin(angle + math.pi) * speed * 0.5))))

    def _handle_sparks(self):
        for spark in self.sparks.copy():
            kill = spark.update()

            spark.render(self.fore_d, offset=self.render_scroll)
            if kill:
                self.sparks.remove(spark)

    def _handle_parts(self):
        self.leaf_spawner.update()
        # Could always separate entity and tile particles by creating two
        # separate lists.
        for part in self.parts.copy():
            if part.asset == AssetAnim.PARTICLE_LEAF:
                part.sin_offset(speed=Vec2((0.035, 0)), amp=Vec2((0.3, 0)))
            if part.anim.done:
                self.parts.remove(part)
            else:
                part.update()
                part.render()

    def _handle_events(self):
        for event in pygame.event.get():
            self._handle_window(event)
            for bind in self.binds:
                bind.check(event)

    def _handle_window(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


Game().run()
