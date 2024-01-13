import os
from abc import ABC, abstractmethod

import pygame

BASE_IMG_PATH = 'data/images/'


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
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0
        self.frame_max = img_dur * len(images) - 1

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            # Loops the frame using modulo.
            self.frame = ((self.frame + 1) % self.frame_max)
        else:
            self.frame = min(self.frame + 1, self.frame_max)
            if self.frame >= self.frame_max:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]


class Event(ABC):
    def __init__(self, code, down_action, up_action=None):
        if type(code) is tuple:
            self.code = code
        else:
            self.code = (code,)
        self.down_action = down_action
        self.up_action = up_action

    @abstractmethod
    def check(self, event, event_types=None):
        raise NotImplementedError


class Key(Event):
    def __init__(self, key, down_action, up_action=None):
        super().__init__(key, down_action, up_action)

    def check(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.code:
                self.down_action()
        elif self.up_action and event.type == pygame.KEYUP:
            if event.key in self.code:
                self.up_action()


class Mouse(Event):
    def __init__(self, button, down_action, up_action=None):
        super().__init__(button, down_action, up_action)

    def check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in self.code:
                self.down_action()
        elif self.up_action and event.type == pygame.MOUSEBUTTONUP:
            if event.button in self.code:
                self.up_action()
