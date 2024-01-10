import pygame

from scripts.tile import Tile
from scripts.vector2 import Vector2

NEIGHBOR_OFFSETS = [(-1, 0),
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (1, 0),
                    (0, 0),
                    (-1, 1),
                    (0, 1),
                    (1, 1)]
# More efficient to look up values in a set than a list, also true for
# dictionaries.
PHYSICS_TILES = {'grass',
                 'stone'}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        for i in range(10):
            grass_v2 = Vector2((3 + i, 10))
            self.tilemap[grass_v2.json()] = Tile('grass', 1, grass_v2)
            stone_v2 = Vector2((10, 5 + i))
            self.tilemap[stone_v2.json()] = Tile('stone', 1, stone_v2)

    def render(self, surf, offset=(0, 0)):
        # Offgrid tiles are often rendered as decorations, therefor we should
        # render them first so that they are applied behind the grid.
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile.type][tile.variant],
                      tile.pos.sub(offset))

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            # The second [] can be performed because the type is a list.
            # Multiply has to be done first for the subtraction to work.
            surf.blit(self.game.assets[tile.type][tile.variant],
                      tile.pos.multiply(self.tile_size).sub(offset).tuple())

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile.type in PHYSICS_TILES:
                rects.append(pygame.Rect(tile.pos.x * self.tile_size,
                                         tile.pos.y * self.tile_size,
                                         self.tile_size,
                                         self.tile_size))
        return rects

    def tiles_around(self, pos):
        tiles = []
        # Using this formula ensures correct index. Otherwise, we may get
        # rounding errors or extra digits.
        tile_loc = (int(pos.x // self.tile_size),
                    int(pos.y // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = Vector2((tile_loc[0] + offset[0],
                                 tile_loc[1] + offset[1])).json()
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
