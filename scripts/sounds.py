from enum import Enum

import pygame


class SoundAmbience(Enum):
    AMBIENCE = 'data/sfx/ambience.wav'


class SoundEffect(Enum):
    DASH = 'data/sfx/dash.wav'
    HIT = 'data/sfx/hit.wav'
    JUMP = 'data/sfx/jump.wav'
    SHOOT = 'data/sfx/shoot.wav'


class SoundMusic(Enum):
    MUSIC = 'data/music.wav'


class Sounds:
    def __init__(self):
        pygame.mixer.init()

        self.ambient = {
            SoundAmbience.AMBIENCE.value: pygame.mixer.Sound(SoundAmbience.AMBIENCE.value),
        }

        self.sfx = {
            SoundEffect.DASH.value: pygame.mixer.Sound(SoundEffect.DASH.value),
            SoundEffect.HIT.value: pygame.mixer.Sound(SoundEffect.HIT.value),
            SoundEffect.JUMP.value: pygame.mixer.Sound(SoundEffect.JUMP.value),
            SoundEffect.SHOOT.value: pygame.mixer.Sound(SoundEffect.SHOOT.value),
        }

        self.ambient[SoundAmbience.AMBIENCE.value].set_volume(0.2)
        self.sfx[SoundEffect.DASH.value].set_volume(0.3)
        self.sfx[SoundEffect.HIT.value].set_volume(0.8)
        self.sfx[SoundEffect.JUMP.value].set_volume(0.7)
        self.sfx[SoundEffect.SHOOT.value].set_volume(0.4)

    def get_ambient(self, sound: SoundAmbience):
        return self.ambient[sound.value]

    def get_sfx(self, sound: SoundEffect):
        return self.sfx[sound.value]

    def load_music(self, music: SoundMusic, volume):
        pygame.mixer.music.load(music.value)
        pygame.mixer.music.set_volume(volume)
        # -1 to loop indefinitely
        pygame.mixer.music.play(-1)
