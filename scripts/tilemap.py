import pygame

from scripts.assets import AssetTile
from scripts.vector2 import Vector2

NEIGHBOR_OFFSETS = ((-1, 0),
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (1, 0),
                    (0, 0),
                    (-1, 1),
                    (0, 1),
                    (1, 1))

PHYSICS_TILES = {AssetTile.GRASS,
                 AssetTile.STONE}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def render(self, surf, offset=(0, 0)):
        # Offgrid tiles are often rendered as decorations, therefor we should
        # render them first so that they are applied behind the grid.
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets.get_tiles(tile.type, tile.variant),
                      tile.pos
                      .sub(offset)
                      .tuple())

        # Optimization to only render tiles that are visible.
        top_left_tile_x = offset[0] // self.tile_size
        top_left_tile_y = offset[1] // self.tile_size
        # Add one to compensate for rounding errors.
        top_right_tile_x = (offset[0] + surf.get_width()) // self.tile_size + 1
        top_right_tile_y = (offset[1] + surf.get_height()) // self.tile_size + 1
        for x in range(top_left_tile_x, top_right_tile_x):
            for y in range(top_left_tile_y, top_right_tile_y):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(
                        self.game.assets.get_tiles(tile.type, tile.variant),
                        tile.pos
                        .multiply(self.tile_size)
                        .sub(offset)
                        .tuple())

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
