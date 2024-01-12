import random

from scripts.vector2 import Vector2


class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = Vector2(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos.x += self.speed

    def render(self, surf, offset=(0, 0)):
        render_pos = self.pos.sub((offset[0] * self.depth,
                                   offset[1] * self.depth))
        surf.blit(self.img,
                  (render_pos.x %
                   (surf.get_width() + self.img.get_width()) -
                   self.img.get_width(),
                   render_pos.y %
                   (surf.get_height() + self.img.get_height()) -
                   self.img.get_height()))


class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []

        for _ in range(count):
            self.clouds.append(Cloud(
                Vector2((random.random() * 99_999, random.random() * 99_999)),
                random.choice(cloud_images),
                random.random() * 0.05 + 0.05,
                random.random() * 0.6 + 0.2))

        self.clouds.sort(key=lambda cloud: cloud.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)
