import json

import pygame

from scripts.assets import AssetTile
from scripts.encoder import Encoder
from scripts.tile import Tile
from scripts.utils import Vec2

NEIGHBOR_OFFSETS = (Vec2((-1, 0)),
                    Vec2((-1, -1)),
                    Vec2((0, -1)),
                    Vec2((1, -1)),
                    Vec2((1, 0)),
                    Vec2((0, 0)),
                    Vec2((-1, 1)),
                    Vec2((0, 1)),
                    Vec2((1, 1)))
PHYSICS_TILES = {AssetTile.GRASS,
                 AssetTile.STONE}
AUTOTILE_TYPES = {AssetTile.GRASS,
                  AssetTile.STONE}
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}


class Tilemap:
    def __init__(self, game, size=16):
        self.game = game
        self.size = size
        self.tilemap = {}
        self.offgrid = []

    def save(self, path):
        f = open(path, 'w')
        json.dump({
            'tilemap': self.tilemap,
            'size': self.size,
            'offgrid': self.offgrid
        }, f, cls=Encoder)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        for tile in map_data['tilemap'].values():
            tile_type = AssetTile[tile['type']]
            tile_var = tile['var']
            tile_pos = Vec2(tile['pos'])
            self.tilemap[tile_pos.json()] = Tile(tile_type,
                                                 tile_var,
                                                 tile_pos)

        self.size = map_data['size']

        for tile in map_data['offgrid']:
            tile_type = AssetTile[tile['type']]
            tile_var = tile['var']
            tile_pos = Vec2(tile['pos'])
            self.offgrid.append(
                Tile(tile_type,
                     tile_var,
                     tile_pos))

    def solid_check(self, pos=Vec2((0, 0))):
        tile_loc = pos.div_f(self.size).int().json()
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc].type in PHYSICS_TILES:
                return self.tilemap[tile_loc]

    def extract(self, pairs, keep=False):
        matches = []
        for tile in self.offgrid.copy():
            if (tile.type, tile.var) in pairs:
                matches.append(tile.deepcopy())
                if not keep:
                    self.offgrid.remove(tile)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile.type, tile.var) in pairs:
                matches.append(tile.deepcopy())
                matches[-1].pos = matches[-1].pos.mult(self.size)
                if not keep:
                    del self.tilemap[loc]

        return matches

    def automap(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = tile.pos.add(shift).json()
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc].type == tile.type:
                        neighbors.add(shift)

            neighbors = tuple(sorted(neighbors))
            if (tile.type in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile.var = AUTOTILE_MAP[neighbors]

    def render(self):
        # Offgrid tiles are often rendered as decorations, therefor we should
        # render them first so that they are applied behind the grid.
        for tile in self.offgrid:
            self.game.fore_d.blit(
                self.game.assets.get_tiles(tile.type, tile.var),
                tile.pos
                .sub(self.game.render_scroll)
                .tuple())

        # Optimization to only render tiles that are visible.
        top_left_tile = self.game.render_scroll.div_f(self.size)
        # Add one to compensate for rounding errors.
        top_right_tile = (self.game.render_scroll
                          .add(self.game.fore_d.get_size())
                          .div_f(self.size)
                          .add((1, 1)))

        for x in range(top_left_tile.x, top_right_tile.x):
            for y in range(top_left_tile.y, top_right_tile.y):
                loc = f'{x};{y}'
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    self.game.fore_d.blit(
                        self.game.assets.get_tiles(tile.type, tile.var),
                        tile.pos
                        .mult(self.size)
                        .sub(self.game.render_scroll)
                        .tuple())

    def physics_rects_around(self, pos=Vec2((0, 0))):
        rects = []
        for tile in self.tiles_around(pos):
            if tile.type in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(*tile.pos.mult(self.size),
                                self.size,
                                self.size))
        return tuple(rects)

    def tiles_around(self, pos=Vec2((0, 0))):
        tiles = []
        # Using this formula ensures correct index. Otherwise, we may get
        # rounding errors or extra digits.
        tile_loc = pos.div_f(self.size).int()
        for offset in NEIGHBOR_OFFSETS:
            check_loc = tile_loc.add(offset).json()
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tuple(tiles)
