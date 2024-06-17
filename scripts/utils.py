import os
from abc import ABC, abstractmethod

import pygame

BASE_IMG_PATH = 'data/images/'


def get_rects(game, type, var, keep, size=(0, 0), offset=(0, 0)):
    spawns = []

    for tile in game.tilemap.extract([(type, var)], keep):
        spawns.append(pygame.Rect(*tile.pos.add(offset), *size))

    return tuple(spawns)


def load_image(path):
    # Using .convert() converts the internal representation of the image to
    # make it more efficient for rendering.
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    # The black background will be rendered as transparent,
    # i.e. one specific color should be rendered transparent.
    img.set_colorkey((0, 0, 0))

    return img


def load_images(path):
    images = []

    # os.listdir() may not work on Linux. Using sorted should make this
    # consistent across all platforms.
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))

    return tuple(images)


class Anim:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.img_dur = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0
        self.frame_max = img_dur * len(images) - 1

    def deepcopy(self):
        return Anim(self.images, self.img_dur, self.loop)

    def update(self):
        if self.loop:
            # Loops the frame using modulo.
            self.frame = (self.frame + 1) % self.frame_max
        else:
            self.frame = min(self.frame + 1, self.frame_max)

            if self.frame >= self.frame_max:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_dur)]


class Dir:
    def __init__(self, left=False, right=False, up=False, down=False):
        self.left = left
        self.right = right
        self.up = up
        self.down = down

    def reset(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def toggle_left(self):
        self.left = not self.left

    def toggle_right(self):
        self.right = not self.right

    def toggle_up(self):
        self.up = not self.up

    def toggle_down(self):
        self.down = not self.down


class Vec2:
    def __init__(self, pos):
        [self.x, self.y] = pos

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError()

    def deepcopy(self):
        return Vec2((self.x, self.y))

    def mult(self, scalar):
        return Vec2((self.x * scalar, self.y * scalar))

    def div(self, scalar):
        return Vec2((self.x / scalar, self.y / scalar))

    def div_f(self, scalar):
        return Vec2((self.x // scalar, self.y // scalar))

    def sub(self, offset):
        return Vec2((self.x - offset[0], self.y - offset[1]))

    def add(self, offset):
        return Vec2((self.x + offset[0], self.y + offset[1]))

    def mod(self, offset):
        return Vec2((self.x % offset[0], self.y % offset[1]))

    def int(self):
        return Vec2((int(self.x), int(self.y)))

    def tuple(self):
        return (self.x, self.y)

    def json(self):
        return f'{self.x};{self.y}'


class Event(ABC):
    def __init__(self, codes, down_action, up_action=None):
        self.codes = codes if type(codes) is tuple else (codes,)
        self.down_action = down_action
        self.up_action = up_action

    @abstractmethod
    def check(self, event, event_types=None):
        raise NotImplementedError


class Key(Event):
    def __init__(self, codes, down_action, up_action=None):
        super().__init__(codes, down_action, up_action)

    def check(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.codes:
                self.down_action()
        elif self.up_action and event.type == pygame.KEYUP:
            if event.key in self.codes:
                self.up_action()


class Mouse(Event):
    def __init__(self, codes, down_action, up_action=None):
        super().__init__(codes, down_action, up_action)

    def check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in self.codes:
                self.down_action()
        elif self.up_action and event.type == pygame.MOUSEBUTTONUP:
            if event.button in self.codes:
                self.up_action()
