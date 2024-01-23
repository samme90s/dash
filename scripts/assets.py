from enum import Enum

from scripts.utils import Anim, load_images


class AssetAnim(Enum):
    ENEMY_IDLE = 'entities/enemy/idle'
    ENEMY_RUN = 'entities/enemy/run'
    PARTICLE_LEAF = 'particles/leaf'
    PARTICLE_DARK = 'particles/dark'
    PLAYER_IDLE = 'entities/player/idle'
    PLAYER_JUMP = 'entities/player/jump'
    PLAYER_RUN = 'entities/player/run'
    PLAYER_SLIDE = 'entities/player/slide'
    PLAYER_Y_SLIDE = 'entities/player/y_slide'


class AssetLayer(Enum):
    BACKGROUND = 'layers/backgrounds'
    CLOUD = 'layers/clouds'


class AssetTile(Enum):
    DECOR = 'tiles/decor'
    GRASS = 'tiles/grass'
    LARGE_DECOR = 'tiles/large_decor'
    SPAWNERS = 'tiles/spawners'
    STONE = 'tiles/stone'


class Assets:
    def __init__(self):
        self.anims = {
            AssetAnim.ENEMY_IDLE.value: Anim(
                load_images(AssetAnim.ENEMY_IDLE.value),
                img_dur=6),
            AssetAnim.ENEMY_RUN.value: Anim(
                load_images(AssetAnim.ENEMY_RUN.value),
                img_dur=4),
            AssetAnim.PARTICLE_LEAF.value: Anim(
                load_images(AssetAnim.PARTICLE_LEAF.value),
                img_dur=20,
                loop=False),
            AssetAnim.PARTICLE_DARK.value: Anim(
                load_images(AssetAnim.PARTICLE_DARK.value),
                img_dur=20,
                loop=False),
            AssetAnim.PLAYER_IDLE.value: Anim(
                load_images(AssetAnim.PLAYER_IDLE.value),
                img_dur=6),
            AssetAnim.PLAYER_JUMP.value: Anim(
                load_images(AssetAnim.PLAYER_JUMP.value)),
            AssetAnim.PLAYER_RUN.value: Anim(
                load_images(AssetAnim.PLAYER_RUN.value),
                img_dur=4),
            AssetAnim.PLAYER_SLIDE.value: Anim(
                load_images(AssetAnim.PLAYER_SLIDE.value)),
            AssetAnim.PLAYER_Y_SLIDE.value: Anim(
                load_images(AssetAnim.PLAYER_Y_SLIDE.value))
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
            AssetTile.SPAWNERS.value: load_images(
                AssetTile.SPAWNERS.value),
            AssetTile.STONE.value: load_images(
                AssetTile.STONE.value)
        }

    def get_anim(self, type: AssetAnim):
        return self.anims[type.value]

    def get_layers(self, type: AssetLayer, var=-1):
        if (var < 0):
            return self.layers[type.value]
        elif var >= 0 and isinstance(self.layers[type.value], tuple):
            return self.layers[type.value][var]

        raise FileNotFoundError()

    def get_tiles(self, type: AssetTile, var=-1):
        if var < 0:
            return self.tiles[type.value]
        elif var >= 0 and isinstance(self.tiles[type.value], tuple):
            return self.tiles[type.value][var]

        raise FileNotFoundError()
