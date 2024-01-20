import math
import random

import pygame

from scripts.utils import Vec2


class Particles:
    def __init__(self,
                 game,
                 tile_type,
                 tile_variant,
                 tile_keep,
                 particle_asset,
                 particle_velocity,
                 particle_random_frame,
                 offset=Vec2((0, 0)),
                 size=Vec2((16, 16)),
                 spawn_rate=40_960):
        # The number decides how often something spawns.
        # >number = less spawns
        self.SPAWN_RATE = spawn_rate
        self.game = game
        self.tile_type = tile_type
        self.tile_variant = tile_variant
        self.tile_keep = tile_keep
        self.particle_asset = particle_asset
        self.particle_velocity = particle_velocity
        self.particle_random_frame = particle_random_frame
        self.offset = offset
        self.size = size
        self.spawns = self.__get_spawners()
        self.particles = []

    def __get_spawners(self):
        spawns = []
        for tile in self.game.tilemap.extract(
                [(self.tile_type, self.tile_variant)],
                self.tile_keep):
            spawns.append(pygame.Rect(*tile.pos.add(self.offset), *self.size))
        return tuple(spawns)

    def update(self):
        for rect in self.spawns:
            if random.random() * self.SPAWN_RATE < rect.width * rect.height:
                self.particles.append(
                    Particle(self.game,
                             self.particle_asset,
                             Vec2((rect.x, rect.y))
                             .add((random.random() * rect.width,
                                  random.random() * rect.height)),
                             self.particle_velocity,
                             self.particle_random_frame))

    def render(self, speed=Vec2((0, 0)), amp=Vec2((0, 0))):
        for particle in self.particles.copy():
            kill = particle.update()
            # speed reduces the speed of the sine curve loop.
            # offset reduces the amplitude of the sine curve.
            particle.pos = particle.pos.add(
                (math.sin(particle.animation.frame * speed.x) * amp.x,
                 math.sin(particle.animation.frame * speed.y) * amp.y))
            particle.render()
            if kill:
                self.particles.remove(particle)


class Particle:
    def __init__(self, game, asset, pos, velocity=(0, 0), random_frame=True):
        self.game = game
        self.asset = asset
        self.pos = pos.deepcopy()
        self.velocity = Vec2(velocity)
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

    def render(self):
        img = self.animation.img()
        self.game.display.blit(
            img,
            self.pos
            .sub((self.game.render_scroll.x + img.get_width() // 2,
                  self.game.render_scroll.y + img.get_height() // 2))
            .tuple())
