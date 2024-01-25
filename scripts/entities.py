import math
import random

import pygame

from scripts.assets import AssetAnim, AssetSprite
from scripts.hitpoint import Hitpoint
from scripts.particle import PartFactory, Particle
from scripts.projectile import Proj
from scripts.sounds import SoundEffect
from scripts.spark import SparkFactory
from scripts.utils import Dir, Vec2


class PhysicsEntity:
    def __init__(self, game, asset, size, pos):
        self.game = game
        self.asset = None
        self.size = size
        self.pos = pos.deepcopy()
        self.hitpoint = Hitpoint(1)
        self.vel = Vec2((0, 0))
        self.vel_f = self.vel.deepcopy()
        self.collisions = Dir()

        # To account for images with padding.
        self.anim_offset = Vec2((-3, -3))
        self.flip = False
        self._set_anim(asset)

    def _set_anim(self, asset):
        if asset != self.asset:
            self.asset = asset
            self.anim = self.game.assets.get_anim(asset).deepcopy()

    def update(self, movement=Vec2((0, 0))):
        self.collisions.reset()
        self._update_vel_f(movement)
        self._handle_flip()
        self._handle_anim()
        # Update each axis independently.
        self._update_pos_x()
        self._update_pos_y()
        self._apply_gravity()
        self._norm_vel_x()

    def _update_vel_f(self, movement):
        self.vel_f = self.vel.add(movement)

    def _handle_flip(self):
        if self.vel_f.x > 0:
            self.flip = False
        if self.vel_f.x < 0:
            self.flip = True

    def _handle_anim(self):
        if self.anim:
            self.anim.update()

    def _update_pos_x(self):
        self.pos.x += self.vel_f.x
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if self.vel_f.x > 0:
                    entity_rect.right = rect.left
                    self.collisions.right = True
                if self.vel_f.x < 0:
                    entity_rect.left = rect.right
                    self.collisions.left = True
                self.pos.x = entity_rect.x

    def _update_pos_y(self):
        self.pos.y += self.vel_f.y
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if self.vel_f.y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions.down = True
                if self.vel_f.y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions.up = True
                self.pos.y = entity_rect.y

    def _apply_gravity(self):
        # Apply gravity, with a terminal vel.
        # Positive y is down (not like a cartesian plane from math).
        self.vel.y = min(5, self.vel.y + 0.1)

        if self.collisions.down or self.collisions.up:
            self.vel.y = 0

    def _norm_vel_x(self):
        if self.vel.x > 0:
            self.vel.x = max(0, self.vel.x - 0.1)
        else:
            self.vel.x = min(0, self.vel.x + 0.1)

    def rect(self):
        return pygame.Rect(*self.pos, *self.size)

    def render(self):
        self.game.fore_d.blit(
            pygame.transform.flip(self.anim.img(), self.flip, False),
            self.pos
            .sub(self.game.render_scroll)
            .add(self.anim_offset)
            .tuple())


class Enemy(PhysicsEntity):
    def __init__(self, game, size, pos):
        super().__init__(game, AssetAnim.ENEMY_IDLE, size, pos)
        self.walking = 0

    def update(self, movement=Vec2((0, 0))):
        if self.walking:
            self._movement_algorithm(movement)
            self._norm_walking()
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        super().update(movement)
        self._update_anim()
        self._check_player_collision()

    def _movement_algorithm(self, movement):
        pos = Vec2((self.rect().centerx + (-7 if self.flip else 7),
                    self.pos.y + 23))
        if not self.game.tilemap.solid_check(pos):
            self.flip = not self.flip

        if not self.collisions.right or self.collisions.left:
            movement.x += (-0.5 if self.flip else 0.5)
        else:
            self.flip = not self.flip

    def _norm_walking(self):
        self.walking = max(0, self.walking - 1)
        if not self.walking:
            diff = Vec2((self.game.player.pos.x - self.pos.x,
                        self.game.player.pos.y - self.pos.y))
            if (abs(diff.y) < 16):
                self._shoot(diff)

    def _shoot(self, diff=Vec2((0, 0))):
        if self.flip and diff.x < 0:
            pos = Vec2((self.rect().centerx - 7, self.rect().centery))
            vel = Vec2((-1.5, 0))
            self.game.projs.append(Proj(pos, vel))
            self._add_shoot_effects()
        elif not self.flip and diff.x > 0:
            pos = Vec2((self.rect().centerx + 7, self.rect().centery))
            vel = Vec2((1.5, 0))
            self.game.projs.append(Proj(pos, vel))
            self._add_shoot_effects()

    def _add_shoot_effects(self):
        self.game.sounds.get_sfx(SoundEffect.SHOOT).play()

    def _update_anim(self):
        if self.vel_f.x != 0:
            self._set_anim(AssetAnim.ENEMY_RUN)
        else:
            self._set_anim(AssetAnim.ENEMY_IDLE)

    def _check_player_collision(self):
        if self.game.player.dashing >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self._add_hit_effects()
                self.hitpoint.reduce(1)

    def _add_hit_effects(self):
        self.game.sounds.get_sfx(SoundEffect.HIT).play()
        self.game.shake = max(16, self.game.shake)
        for spark in SparkFactory.burst(Vec2(self.rect().center)):
            self.game.sparks.append(spark)
        for part in PartFactory.burst(self.game, AssetAnim.PARTICLE_DARK, Vec2(self.rect().center)):
            self.game.parts.append(part)
        self.game.sparks.append(SparkFactory.line(self.pos, 0))
        self.game.sparks.append(SparkFactory.line(self.pos, math.pi))

    def render(self):
        super().render()

        gun_img = self.game.assets.get_sprite(AssetSprite.GUN)
        if self.flip:
            self.game.fore_d.blit(
                pygame.transform.flip(gun_img, True, False),
                (self.rect().centerx - 4 - gun_img.get_width() - self.game.render_scroll.x,
                 self.rect().centery - self.game.render_scroll.y))
        else:
            self.game.fore_d.blit(
                gun_img,
                (self.rect().centerx + 4 - self.game.render_scroll.x,
                 self.rect().centery - self.game.render_scroll.y))


class Player(PhysicsEntity):
    def __init__(self, game, size, pos):
        super().__init__(game, AssetAnim.PLAYER_IDLE, size, pos)
        self.in_air = True
        self.air_time = 0
        self.jumps_max = 2
        self.jumps = self.jumps_max
        self.y_slide = False

        self.dashing = 0
        self.dashing_dur = 12
        self.dashing_max = 60
        self.dashing_diff = self.dashing_max - self.dashing_dur
        self.dashing_thresholds = {
            self.dashing_max,
            self.dashing_diff
        }

    def update(self, movement=Vec2((0, 0))):
        super().update(movement)
        if self.collisions.down:
            self.in_air = False
            self.air_time = 0
            self.jumps = self.jumps_max
        elif not self.collisions.right and not self.collisions.left:
            self.in_air = True
            self.air_time += 1

        if self.air_time > 300:
            self.air_time = 0
            self.game.dead += 1

        self.y_slide = False
        if (self.collisions.right or self.collisions.left) and self.in_air:
            self.y_slide = True
            self.vel.y = min(0.5, self.vel.y)
            self._set_anim(AssetAnim.PLAYER_Y_SLIDE)

        self._handle_dash()
        self._update_anim()

    def _handle_dash(self):
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
            if self.dashing in self.dashing_thresholds:
                for part in PartFactory.burst2(self.game, AssetAnim.PARTICLE_DARK, Vec2(self.rect().center)):
                    self.game.parts.append(part)

        if self.dashing > self.dashing_diff:
            self.vel.x = (-8 if self.flip else 8)
            # Slow down the dash more rapidly at the end.
            if self.dashing == self.dashing_diff + 1:
                self.vel.x *= 0.4

            # Acts as a trail of particles following the player.
            self.game.parts.append(
                Particle(game=self.game,
                         asset=AssetAnim.PARTICLE_DARK,
                         pos=Vec2(self.rect().center),
                         vel=self.vel.div(4),
                         rand_f=True))

    def _update_anim(self):
        if not self.y_slide:
            if self.in_air and self.air_time > self.anim.img_dur:
                self._set_anim(AssetAnim.PLAYER_JUMP)
            elif self.dashing > self.dashing_max - self.dashing_dur:
                self._set_anim(AssetAnim.PLAYER_SLIDE)
            elif self.vel_f.x != 0:
                self._set_anim(AssetAnim.PLAYER_RUN)
            else:
                self._set_anim(AssetAnim.PLAYER_IDLE)

    def jump(self):
        if self.y_slide:
            self._y_slide()
        elif self.jumps:
            self._bump(Vec2((0, -3)))

    def _y_slide(self):
        if self.flip and self.vel_f.x < 0:
            self._bump(Vec2((2.5, -2.5)))
        elif not self.flip and self.vel_f.x > 0:
            self._bump(Vec2((-2.5, -2.5)))

    def _bump(self, vec=Vec2((0, -2.5))):
        self.game.sounds.get_sfx(SoundEffect.JUMP).play()
        self.in_air = True
        self.jumps = max(0, self.jumps - 1)
        self.vel.x = vec.x
        self.vel.y = vec.y

    def dash(self):
        if not self.dashing:
            self.game.sounds.get_sfx(SoundEffect.DASH).play()
            self.dashing = self.dashing_max
