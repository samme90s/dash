from scripts.tile import Tile


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        for i in range(10):
            self.tilemap[str(3 + i) + ';10'] = Tile('grass', 1, (3 + i, 10))
            self.tilemap['10;' + str(5 + i)] = Tile('stone', 1, (10, 5 + i))

    def render(self, surf):
        # Offgrid tiles are often rendered as decorations, therefor we should
        # render them first so that they are applied behind the grid.
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile.type][tile.variant],
                      tile.pos)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            # The second [] can be performed because the type is a list.
            surf.blit(self.game.assets[tile.type][tile.variant],
                      ((tile.pos[0] * self.tile_size),
                      (tile.pos[1] * self.tile_size)))
