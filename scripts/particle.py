import random


class Particle:
    def __init__(self, game, asset, pos, velocity=[0, 0], random_frame=True):
        self.game = game
        self.asset = asset
        self.pos = pos.deepcopy()
        self.velocity = list(velocity)
        self.animation = self.game.assets.get_anim(asset).deepcopy()
        if random_frame:
            # Reduce by one to avoid the last frame being selected.
            self.animation.frame = random.randint(0,
                                                  len(self.animation.images) *
                                                  (self.animation.img_duration -
                                                   1))

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos = self.pos.add(self.velocity)

        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, self.pos
                  .sub((offset[0] + img.get_width() // 2,
                        offset[1] + img.get_height() // 2))
                  .tuple())
