import random

from scripts.utils import Vec2


class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = Vec2(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos.x += self.speed

    def render(self, surf, offset=Vec2((0, 0))):
        # Multiplying depth with offset will give a parallax effect.
        render_pos = self.pos.sub(offset.mult(self.depth))

        # Mod the image's dimensions (not removed before it is off-screen).
        # Subtract the image's dimensions (add clouds off-screen)
        surf.blit(self.img,
                  render_pos
                  .mod((surf.get_width() + self.img.get_width(),
                        surf.get_height() + self.img.get_height()))
                  .sub((self.img.get_width(), self.img.get_height()))
                  .tuple())


class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []

        for _ in range(count):
            self.clouds.append(Cloud(
                Vec2((random.random() * 1024, random.random() * 1024)),
                random.choice(cloud_images),
                random.random() * 0.05 + 0.05,
                random.random() * 0.6 + 0.2))

        # This ensures that clouds are rendered in correct order.
        self.clouds.sort(key=lambda cloud: cloud.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=Vec2((0, 0))):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)
