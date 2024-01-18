import random

from scripts.utils import Vector2


class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = Vector2(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos.x += self.speed

    def render(self, surf, offset=(0, 0)):
        # Multiplying depth with offset will give a parallax effect.
        render_pos = self.pos.sub((offset[0] * self.depth,
                                   offset[1] * self.depth))

        surf.blit(self.img,
                  render_pos
                  # Clouds are never removed, thus we utilize a trick looping
                  # them. When looping thing in computer graphics you generally
                  # use modulo.
                  # We add the image's dimensions to make sure the cloud is not
                  # removed before it is off-screen.
                  .mod((surf.get_width() + self.img.get_width(),
                        surf.get_height() + self.img.get_height()))
                  # We subtract the image's dimensions to make sure the clouds
                  # are added off-screen.
                  .sub((self.img.get_width(), self.img.get_height()))
                  .tuple())


class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []

        for _ in range(count):
            self.clouds.append(Cloud(
                Vector2((random.random() * 1024, random.random() * 1024)),
                random.choice(cloud_images),
                random.random() * 0.05 + 0.05,
                random.random() * 0.6 + 0.2))

        # This ensures that clouds are rendered in correct order.
        self.clouds.sort(key=lambda cloud: cloud.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)
