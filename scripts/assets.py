from enum import Enum

from scripts.utils import Animation, load_images


class AssetAnim(Enum):
    PARTICLE_LEAF = 'particles/leaf'
    PLAYER_IDLE = 'entities/player/idle'
    PLAYER_JUMP = 'entities/player/jump'
    PLAYER_RUN = 'entities/player/run'
    PLAYER_SLIDE = 'entities/player/slide'
    PLAYER_WALL_SLIDE = 'entities/player/wall_slide'


class AssetLayer(Enum):
    BACKGROUND = 'layers/backgrounds'
    CLOUD = 'layers/clouds'


class AssetTile(Enum):
    DECOR = 'tiles/decor'
    GRASS = 'tiles/grass'
    LARGE_DECOR = 'tiles/large_decor'
    STONE = 'tiles/stone'


class Assets:
    def __init__(self):
        self.anims = {
            AssetAnim.PARTICLE_LEAF.value: Animation(
                load_images(AssetAnim.PARTICLE_LEAF.value),
                img_dur=20,
                loop=False),
            AssetAnim.PLAYER_IDLE.value: Animation(
                load_images(AssetAnim.PLAYER_IDLE.value),
                img_dur=6),
            AssetAnim.PLAYER_JUMP.value: Animation(
                load_images(AssetAnim.PLAYER_JUMP.value)),
            AssetAnim.PLAYER_RUN.value: Animation(
                load_images(AssetAnim.PLAYER_RUN.value),
                img_dur=4),
            AssetAnim.PLAYER_SLIDE.value: Animation(
                load_images(AssetAnim.PLAYER_SLIDE.value)),
            AssetAnim.PLAYER_WALL_SLIDE.value: Animation(
                load_images(AssetAnim.PLAYER_WALL_SLIDE.value))
        }
        self.layers = {
            AssetLayer.BACKGROUND.value: load_images(
                AssetLayer.BACKGROUND.value),
            AssetLayer.CLOUD.value: load_images(
                AssetLayer.CLOUD.value)
        }
        self.tiles = {
            AssetTile.DECOR.value: load_images(
                AssetTile.DECOR.value),
            AssetTile.GRASS.value: load_images(
                AssetTile.GRASS.value),
            AssetTile.LARGE_DECOR.value: load_images(
                AssetTile.LARGE_DECOR.value),
            AssetTile.STONE.value: load_images(
                AssetTile.STONE.value)
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
