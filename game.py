import sys

import pygame

from instance import Instance
from scripts.assets import AssetAnim, AssetLayer, AssetSprite, AssetTile
from scripts.clouds import Clouds
from scripts.entities import Enemy, Player
from scripts.particle import ParticleSpawner
from scripts.utils import Key, Vec2, get_rects


class Game(Instance):
    def __init__(self):
        super().__init__(title='python',
                         map_path='map.json',
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

        self.clouds = Clouds(self.assets.get_layers(AssetLayer.CLOUD), count=16)
        self.player = Player(self, (8, 15), Vec2((50, 50)))

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
            spawn_r=0.02)

        stone_rects = get_rects(
            game=self,
            type=AssetTile.STONE,
            var=1,
            keep=True,
            size=Vec2((16, 8)),
            offset=Vec2((0, 0)))
        self.dark_spawner = ParticleSpawner(
            game=self,
            asset=AssetAnim.PARTICLE_DARK,
            vel=Vec2((0, -0.3)),
            rand_f=True,
            rects=stone_rects,
            spawn_r=0.002)
        self.projs = []
        self.parts = []
        self.enemies = []
        for spawn in self.tilemap.extract(
            [(AssetTile.SPAWNERS, 0),
             (AssetTile.SPAWNERS, 1)]):
            if spawn.var == 0:
                self.player.pos = spawn.pos
            else:
                self.enemies.append(Enemy(self, (8, 15), spawn.pos))

    def run(self):
        while True:
            # Order is important here!
            self._clear()
            self._handle_scroll()
            self._handle_clouds()
            self._handle_tilemap()
            self._handle_enemies()
            self._handle_player()
            self._handle_projs()
            self._handle_parts()
            self._handle_events()
            self._render()

    def _clear(self):
        super()._clear()
        self.back_d.blit(
            self.assets.get_layers(AssetLayer.BACKGROUND, 0), (0, 0))

    def _handle_scroll(self):
        self.scroll = self.scroll.add(((self.player.rect().centerx
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

    def _handle_player(self):
        self.player.update(
            Vec2((self.dir.right - self.dir.left,
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
            elif self.player.dashing_dur < 50:
                if self.player.rect().collidepoint(proj[0].tuple()):
                    self.projs.remove(proj)

    def _handle_parts(self):
        self.leaf_spawner.update()
        self.dark_spawner.update()
        # Could always separate entity and tile particles by creating two
        # separate lists.
        for part in self.parts.copy():
            if part.asset == AssetAnim.PARTICLE_LEAF:
                part.sin_offset(speed=Vec2((0.035, 0)), amp=Vec2((0.3, 0)))
            if part.asset == AssetAnim.PARTICLE_DARK:
                part.sin_offset(speed=Vec2((0.1, 0)), amp=Vec2((0.3, 0)))
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
