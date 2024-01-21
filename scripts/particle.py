import math
import random

from scripts.utils import Vec2


def get_parts_burst(game, amount, asset, pos, rand_f):
    parts = []
    for _ in range(amount):
        angle = random.random() * math.pi * 2
        speed = random.random() * 0.5 + 0.5
        vel = Vec2((math.cos(angle) * speed, math.sin(angle) * speed))
        parts.append(Particle(game, asset, pos, vel, rand_f))

    return tuple(parts)


class ParticleSpawner:
    def __init__(self, game, asset, vel, rand_f, rects, spawn_r=0.01):
        self.game = game
        self.asset = asset
        self.vel = vel
        self.rand_f = rand_f
        self.rects = rects
        self.spawn_r = spawn_r

    def update(self):
        for rect in self.rects:
            if (random.random() * 1) < self.spawn_r:
                pos = Vec2((rect.x + random.random() * rect.width,
                            rect.y + random.random() * rect.height))
                self.game.parts.append(
                    Particle(self.game,
                             self.asset,
                             pos,
                             self.vel,
                             self.rand_f))


class Particle:
    def __init__(self, game, asset, pos, vel=(0, 0), rand_f=True):
        self.game = game
        self.asset = asset
        self.pos = pos.deepcopy()
        self.vel = Vec2(vel)
        self.anim = self.game.assets.get_anim(asset).deepcopy()
        if rand_f:
            # Reduce by one to avoid the last frame being selected.
            self.anim.frame = random.randint(
                0, len(self.anim.images) * (self.anim.img_dur - 1))

    def sin_offset(self, speed=Vec2((0, 0)), amp=Vec2((0, 0))):
        self.pos = self.pos.add((math.sin(self.anim.frame * speed.x) * amp.x,
                                 math.sin(self.anim.frame * speed.y) * amp.y))

    def update(self):
        self.pos = self.pos.add(self.vel)
        self.anim.update()

        return self.anim.done

    def render(self):
        img = self.anim.img()
        self.game.display.blit(
            img,
            self.pos
            .sub((self.game.render_scroll.x + img.get_width() // 2,
                  self.game.render_scroll.y + img.get_height() // 2))
            .tuple())
