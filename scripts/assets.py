from enum import Enum

from scripts.utils import Animation, load_images


class AssetAnim(Enum):
    PLAYER_IDLE = 'player/idle'
    PLAYER_JUMP = 'player/jump'
    PLAYER_RUN = 'player/run'
    PLAYER_SLIDE = 'player/slide'
    PLAYER_WALL_SLIDE = 'player/wall_slide'


class AssetLayer(Enum):
    BACKGROUND = 'background'
    CLOUD = 'cloud'


class AssetTile(Enum):
    DECOR = 'decor'
    GRASS = 'grass'
    LARGE_DECOR = 'large_decor'
    STONE = 'stone'


class Assets:
    def __init__(self):
        self.anims = {
            'player/idle': Animation(
                load_images('entities/player/idle'), img_dur=6),
            'player/jump': Animation(
                load_images('entities/player/jump')),
            'player/run': Animation(
                load_images('entities/player/run'), img_dur=4),
            'player/slide': Animation(
                load_images('entities/player/slide')),
            'player/wall_slide': Animation(
                load_images('entities/player/wall_slide'))
        }
        self.layers = {
            'background': load_images('layers/backgrounds'),
            'cloud': load_images('layers/clouds')
        }
        self.tiles = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone')
        }

    def get_anim(self, type: AssetAnim):
        return self.anims[type.value]

    def get_layers(self, type: AssetLayer, variant=-1):
        if (variant < 0):
            return self.layers[type.value]
        elif variant >= 0 and isinstance(self.layers[type.value], list):
            return self.layers[type.value][variant]

        raise FileNotFoundError()

    def get_tiles(self, type: AssetTile, variant=-1):
        if variant < 0:
            return self.tiles[type.value]
        elif variant >= 0 and isinstance(self.tiles[type.value], list):
            return self.tiles[type.value][variant]

        raise FileNotFoundError()
