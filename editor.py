import sys

import pygame

from scripts.assets import Assets, AssetTile
from scripts.tile import Tile
from scripts.tilemap import Tilemap
from scripts.utils import Key, Mouse
from scripts.vector2 import Vector2

RENDER_SCALE = 2.0


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = Assets()

        self.movement = [False, False, False, False]

        self.binds = (
            Key((pygame.K_a, pygame.K_LEFT),
                lambda: self._set_movement(0, True),
                lambda: self._set_movement(0, False)),
            Key((pygame.K_d, pygame.K_RIGHT),
                lambda: self._set_movement(1, True),
                lambda: self._set_movement(1, False)),
            Key((pygame.K_w, pygame.K_UP),
                lambda: self._set_movement(2, True),
                lambda: self._set_movement(2, False)),
            Key((pygame.K_s, pygame.K_DOWN),
                lambda: self._set_movement(3, True),
                lambda: self._set_movement(3, False)),
            Key(pygame.K_g,
                lambda: self._toggle_ongrid()),
            Key(pygame.K_t,
                lambda: self.tilemap.automap()),
            Key(pygame.K_o,
                lambda: self.tilemap.save('map.json')),
            Key(pygame.K_TAB,
                lambda: self._scroll_tile_type(1)),
            Mouse(1,
                  lambda: self._set_clicking(True),
                  lambda: self._set_clicking(False)
                  ),
            Mouse(3,
                  lambda: self._set_right_clicking(True),
                  lambda: self._set_right_clicking(False)),
            Mouse(4,
                  lambda: self._scroll_tile_variant(1)),
            Mouse(5,
                  lambda: self._scroll_tile_variant(-1)))

        self.tilemap = Tilemap(self, tile_size=16)
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]
        self.render_scroll = [0, 0]

        self.tile_group = 0
        self.tile_type = tuple(AssetTile)[self.tile_group]
        self.tile_variant = 0
        self.tile_pos = Vector2((0, 0))

        self.mpos = (0, 0)
        self.clicking = False
        self.right_clicking = False
        self.ongrid = True

    def _set_movement(self, index, bool):
        self.movement[index] = bool

    def _set_clicking(self, bool):
        self.clicking = bool
        if not self.ongrid:
            self.tilemap.offgrid_tiles.append(
                Tile(self.tile_type,
                     self.tile_variant,
                     Vector2((self.mpos[0] + self.scroll[0],
                              self.mpos[1] + self.scroll[1]))))

    def _set_right_clicking(self, bool):
        self.right_clicking = bool

    def _toggle_ongrid(self):
        self.ongrid = not self.ongrid

    def _scroll_tile_type(self, amount):
        self.tile_group = (self.tile_group + amount) % len(AssetTile)
        self.tile_type = tuple(AssetTile)[self.tile_group]
        self.tile_variant = 0

    def _scroll_tile_variant(self, amount):
        self.tile_variant = ((self.tile_variant + amount) %
                             len(self.assets.get_tiles(self.tile_type)))

    def run(self):
        while True:
            # Order is important here!
            self._clear()
            self._handle_scroll()
            self._handle_tilemap()
            self._handle_positions()
            self._handle_tile_preview()
            self._handle_tile_placement()
            self._handle_tile_removal()
            self._handle_events()

            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def _clear(self):
        self.display.fill((0, 0, 0))

    def _handle_scroll(self):
        self.scroll[0] += (self.movement[1] - self.movement[0]) * 5
        self.scroll[1] += (self.movement[3] - self.movement[2]) * 5
        self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

    def _handle_tilemap(self):
        self.tilemap.render(self.display, offset=self.render_scroll)

    def _handle_positions(self):
        self.mpos = pygame.mouse.get_pos()
        self.mpos = (self.mpos[0] / RENDER_SCALE,
                     self.mpos[1] / RENDER_SCALE)
        self.tile_pos = Vector2((int((self.mpos[0] + self.scroll[0]) //
                                     self.tilemap.tile_size),
                                 int((self.mpos[1] + self.scroll[1]) //
                                     self.tilemap.tile_size)))

    def _handle_tile_preview(self):
        current_tile_img = self.assets.get_tiles(
            self.tile_type,
            self.tile_variant).copy()
        current_tile_img.set_alpha(155)
        if self.ongrid:
            self.display.blit(current_tile_img,
                              self.tile_pos
                              .multiply(self.tilemap.tile_size)
                              .sub(self.scroll)
                              .tuple())
        else:
            self.display.blit(current_tile_img,
                              self.mpos)

        self.display.blit(current_tile_img,
                          (5, 5))

    def _handle_tile_placement(self):
        if self.clicking and self.ongrid:
            self.tilemap.tilemap[self.tile_pos.json()] = Tile(
                self.tile_type,
                self.tile_variant,
                self.tile_pos)

    def _handle_tile_removal(self):
        if self.right_clicking:
            tile_loc = self.tile_pos.json()
            if tile_loc in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_loc]
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_img = self.assets.get_tiles(tile.type, tile.variant)
                tile_r = pygame.Rect(*tile.pos.sub(self.scroll),
                                     *tile_img.get_size())
                if tile_r.collidepoint(self.mpos):
                    self.tilemap.offgrid_tiles.remove(tile)

    def _handle_events(self):
        for event in pygame.event.get():
            self._handle_window(event)
            for bind in self.binds:
                bind.check(event)

    def _handle_window(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


Editor().run()
