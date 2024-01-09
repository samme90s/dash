import pygame

BASE_IMG_PATH = 'data/images/'


def load_image(path):
    # Using .convert() converts the internal representation of the image to
    # make it more efficient for rendering.
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    # The black background will be rendered as transparent,
    # i.e. one specfic color should be rendered transparent.
    img.set_colorkey((0, 0, 0))
    return img
