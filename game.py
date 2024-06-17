import math
import os
import sys

import pygame

from instance import Instance
from scripts.assets import AssetAnim, AssetLayer, AssetSprite, AssetTile
from scripts.clouds import Clouds
from scripts.entities import Enemy, Player
from scripts.particle import PartFactory, ParticleSpawner
from scripts.sounds import SoundAmbience, SoundEffect, SoundMusic, Sounds
from scripts.spark import SparkFactory
from scripts.utils import Key, Vec2, get_rects


class Game(Instance):
    def __init__(self):
        super().__init__(title='python', res_base=(320, 180), res_scale=3.0)

        self.binds = (
            Key((pygame.K_a, pygame.K_LEFT), lambda: self.dir.toggle_left(), lambda: self.dir.toggle_left()),
            Key((pygame.K_d, pygame.K_RIGHT), lambda: self.dir.toggle_right(), lambda: self.dir.toggle_right()),
            Key((pygame.K_SPACE, pygame.K_UP), lambda: self.player.jump()),
            Key(pygame.K_LSHIFT, lambda: self.player.dash())
        )

        self.sounds = Sounds()
        self.clouds = Clouds(self.assets.get_layers(AssetLayer.CLOUD), count=16)
        self.level = 0

    def run(self):
        self.load_level(self.level)
        self.sounds.load_music(SoundMusic.MUSIC, 0.5)
        self.sounds.get_ambient(SoundAmbience.AMBIENCE).play(-1)

        while True:
            # Order is important here!
            self.clear()
            self.handle_game_state()
            self.handle_scroll()
            self.handle_clouds()
            self.handle_tilemap()
            self.handle_enemies()
            self.handle_player()
            self.handle_projs()
            self.handle_sparks()
            self.handle_parts()
            self.handle_transition()
            self.handle_events()
            self.render()

    def load_level(self, map_id):
        super().load_level(map_id)
        tree_rects = get_rects(self, AssetTile.LARGE_DECOR, 2, True, Vec2((23, 13)), Vec2((4, 4)))
        self.leaf_spawner = ParticleSpawner(self, AssetAnim.PARTICLE_LEAF, Vec2((-0.1, 0.3)), True, tree_rects, 0.016)

        self.player = Player(self, (8, 15), Vec2((0, 0)))
        self.enemies = []
        self.parts = []
        self.projs = []
        self.sparks = []
        self.transition = -30
        self.handle_spawners()

    def handle_spawners(self):
        for spawn in self.tilemap.extract([(AssetTile.SPAWNERS, 0), (AssetTile.SPAWNERS, 1)]):
            if spawn.var == 0:
                self.player.pos = spawn.pos
            else:
                self.enemies.append(Enemy(self, (8, 15), spawn.pos))

    def clear(self):
        super().clear()
        self.back_d.blit(self.assets.get_layers(AssetLayer.BACKGROUND, 0), (0, 0))

    def handle_game_state(self):
        if self.player.hitpoint.is_dead():
            self.transition = min(30, self.transition + 1)

            if self.transition >= 30:
                self.load_level(self.level)

        if not len(self.enemies):
            self.transition += 1

            if self.transition > 30:
                self.level = min(len(os.listdir('data/maps/')) - 1, self.level + 1)
                self.load_level(self.level)

        if self.transition < 0:
            self.transition += 1

    def handle_scroll(self):
        self.scroll = self.scroll.add(
            ((self.player.rect().centerx - self.fore_d.get_width() / 2 - self.scroll.x) / 30,
             (self.player.rect().centery - self.fore_d.get_height() / 2 - self.scroll.y) / 30)
        )
        self.render_scroll = self.scroll.int()

    def handle_clouds(self):
        self.clouds.update()
        self.clouds.render(self.back_d, offset=self.render_scroll)

    def handle_tilemap(self):
        self.tilemap.render()

    def handle_enemies(self):
        for enemy in self.enemies.copy():
            enemy.update(Vec2((0, 0)))
            enemy.render()

            if enemy.hitpoint.is_dead():
                self.enemies.remove(enemy)

    def handle_player(self):
        if not self.player.hitpoint.is_dead():
            self.player.update(Vec2((self.dir.right - self.dir.left, self.dir.down - self.dir.up)))
            self.player.render()

    def handle_projs(self):
        for proj in self.projs.copy():
            proj.pos = proj.pos.add(proj.vel)
            proj.timer += 1
            img = self.assets.get_sprite(AssetSprite.PROJECTILE)
            pos = (proj.pos.sub((img.get_width() / 2, img.get_height() / 2)).sub(self.render_scroll).tuple())
            self.fore_d.blit(img, pos)

            if self.tilemap.solid_check(proj.pos) or proj.timer > 360:
                self.handle_proj_solid(proj)
            elif (self.player.dashing < self.player.dashing_diff and self.player.rect().collidepoint(proj.pos.tuple())):
                self.handle_proj_hit(proj)

    def handle_proj_solid(self, proj):
        self.projs.remove(proj)

        for spark in SparkFactory.cone(proj.pos, (math.pi if proj.vel.x > 0 else 0)):
            self.sparks.append(spark)

    def handle_proj_hit(self, proj):
        self.projs.remove(proj)
        self.sounds.get_sfx(SoundEffect.HIT).play()
        self.shake = max(48, self.shake)
        self.player.hitpoint.reduce(1)

        for spark in SparkFactory.burst(Vec2(self.player.rect().center)):
            self.sparks.append(spark)

        for part in PartFactory.burst(self, AssetAnim.PARTICLE_DARK, Vec2(self.player.rect().center)):
            self.parts.append(part)

    def handle_sparks(self):
        for spark in self.sparks.copy():
            if not spark.update():
                spark.render(self.fore_d, offset=self.render_scroll)
            else:
                self.sparks.remove(spark)

    def handle_parts(self):
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

    def handle_transition(self):
        if self.transition:
            transition_surf = pygame.Surface(self.fore_d.get_size())
            pygame.draw.circle(
                surface=transition_surf,
                color=(255, 255, 255),
                center=(self.fore_d.get_width() // 2, self.fore_d.get_height() // 2),
                radius=(30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.fore_d.blit(transition_surf, (0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_window(event)

            for bind in self.binds:
                bind.check(event)

    def handle_window(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


Game().run()
