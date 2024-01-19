import sys

import pygame

from app import App
from scripts.assets import AssetTile
from scripts.tile import Tile
from scripts.utils import Key, Mouse, Vec2


class Editor(App):
    def __init__(self):
        super().__init__(title='editor',
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
            Key((pygame.K_w, pygame.K_UP),
                lambda: self.direction.toggle_up(),
                lambda: self.direction.toggle_up()),
            Key((pygame.K_s, pygame.K_DOWN),
                lambda: self.direction.toggle_down(),
                lambda: self.direction.toggle_down()),
            Key(pygame.K_g,
                lambda: self._toggle_ongrid()),
            Key(pygame.K_t,
                lambda: self.tilemap.automap()),
            Key(pygame.K_o,
                lambda: self.tilemap.save('map.json')),
            Key(pygame.K_TAB,
                lambda: self._scroll_tile_type(1)),
            Mouse(1,
                  lambda: self._toggle_click(),
                  lambda: self._toggle_click()
                  ),
            Mouse(3,
                  lambda: self._toggle_r_click(),
                  lambda: self._toggle_r_click()),
            Mouse(4,
                  lambda: self._scroll_tile_variant(1)),
            Mouse(5,
                  lambda: self._scroll_tile_variant(-1)))

        self.tile_group = 0
        self.tile_type = tuple(AssetTile)[self.tile_group]
        self.tile_variant = 0
        self.tile_pos = Vec2((0, 0))

        self.mpos = Vec2((0, 0))
        self.click = False
        self.r_click = False
        self.ongrid = True

    def _toggle_click(self):
        self.click = not self.click
        # This prevents accidental placement of multiple instances.
        if bool and not self.ongrid:
            self.tilemap.offgrid_tiles.append(
                Tile(self.tile_type,
                     self.tile_variant,
                     self.mpos.add(self.scroll)))

    def _toggle_r_click(self):
        self.r_click = not self.r_click

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
            self._render()

    def _clear(self):
        self.display.fill((0, 0, 0))

    def _handle_scroll(self):
        self.scroll = self.scroll.add(((self.direction.right -
                                       self.direction.left) * 5,
                                       (self.direction.down -
                                       self.direction.up) * 5))
        self.render_scroll = self.scroll.int()

    def _handle_tilemap(self):
        self.tilemap.render()

    def _handle_positions(self):
        self.mpos = Vec2(pygame.mouse.get_pos()).div(self.RES_SCALE)
        self.tile_pos = (self.mpos
                         .add(self.scroll)
                         .div_f(self.tilemap.tile_size)
                         .int())

    def _handle_tile_preview(self):
        current_tile_img = self.assets.get_tiles(
            self.tile_type,
            self.tile_variant).copy()
        current_tile_img.set_alpha(155)
        if self.ongrid:
            self.display.blit(current_tile_img,
                              self.tile_pos
                              .mult(self.tilemap.tile_size)
                              .sub(self.scroll)
                              .tuple())
        else:
            self.display.blit(current_tile_img, self.mpos.tuple())

        self.display.blit(current_tile_img, (5, 5))

    def _handle_tile_placement(self):
        if self.click and self.ongrid:
            self.tilemap.tilemap[self.tile_pos.json()] = Tile(
                self.tile_type,
                self.tile_variant,
                self.tile_pos)

    def _handle_tile_removal(self):
        if self.r_click:
            tile_loc = self.tile_pos.json()
            if tile_loc in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_loc]
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_img = self.assets.get_tiles(tile.type, tile.variant)
                tile_r = pygame.Rect(*tile.pos.sub(self.scroll),
                                     *tile_img.get_size())
                if tile_r.collidepoint(self.mpos.tuple()):
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
