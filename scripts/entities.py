import pygame

from scripts.assets import AssetAnim
from scripts.particle import Particle, get_parts_burst
from scripts.utils import Direction, Vec2


class PhysicsEntity:
    def __init__(self, game, asset, size, pos):
        self.game = game
        self.asset = None
        self.size = size
        self.pos = pos.deepcopy()
        self.velocity = Vec2((0, 0))
        self.velocity_f = self.velocity.deepcopy()
        self.collisions = Direction()

        # To account for images with padding.
        self.anim_offset = Vec2((-3, -3))
        self.flip = False
        self._set_anim(asset)

    def _set_anim(self, asset):
        if asset != self.asset:
            self.asset = asset
            self.anim = self.game.assets.get_anim(asset).deepcopy()

    def update(self):
        self.collisions.reset()
        self._update_velocity()
        self._handle_flip()
        self._handle_anim()
        # Update each axis independently.
        self._update_pos_x()
        self._update_pos_y()
        self._apply_gravity()

    def _update_velocity(self):
        self.velocity_f = self.velocity.add(
            (self.game.direction.right - self.game.direction.left,
             self.game.direction.down - self.game.direction.up))

    def _handle_flip(self):
        if self.velocity_f.x > 0:
            self.flip = False
        if self.velocity_f.x < 0:
            self.flip = True

    def _handle_anim(self):
        if self.anim:
            self.anim.update()

    def _update_pos_x(self):
        self.pos.x += self.velocity_f.x
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if self.velocity_f.x > 0:
                    entity_rect.right = rect.left
                    self.collisions.right = True
                if self.velocity_f.x < 0:
                    entity_rect.left = rect.right
                    self.collisions.left = True
                self.pos.x = entity_rect.x

    def _update_pos_y(self):
        self.pos.y += self.velocity_f.y
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if self.velocity_f.y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions.down = True
                if self.velocity_f.y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions.up = True
                self.pos.y = entity_rect.y

    def _apply_gravity(self):
        # Apply gravity, with a terminal velocity.
        # Positive y is down (not like a cartesian plane from math).
        self.velocity.y = min(5, self.velocity.y + 0.1)

        if self.collisions.down or self.collisions.up:
            self.velocity.y = 0

    def rect(self):
        return pygame.Rect(*self.pos, *self.size)

    def render(self):
        self.game.display.blit(
            pygame.transform.flip(self.anim.img(), self.flip, False),
            self.pos
            .sub(self.game.render_scroll)
            .add(self.anim_offset)
            .tuple())


class Player(PhysicsEntity):
    def __init__(self, game, size, pos):
        super().__init__(game, AssetAnim.PLAYER_IDLE, size, pos)
        self.in_air = True
        self.jumps_max = 2
        self.jumps = self.jumps_max
        self.y_slide = False

        self.dashing = 0
        self.dashing_dur = 12
        self.dashing_max = 60

    def update(self):
        super().update()
        if self.collisions.down:
            self.in_air = False
            self.jumps = self.jumps_max

        self.y_slide = False
        if (self.collisions.right or self.collisions.left) and self.in_air:
            self.y_slide = True
            self.velocity.y = min(0.5, self.velocity.y)
            self._set_anim(AssetAnim.PLAYER_Y_SLIDE)

        self._handle_dash()
        self._update_anim()
        self._norm_vel()

    def _handle_dash(self):
        if self.dashing > 0:
            if self.dashing in {self.dashing_max,
                                self.dashing_max - self.dashing_dur}:
                for part in get_parts_burst(game=self.game,
                                            amount=20,
                                            asset=AssetAnim.PARTICLE_DARK,
                                            pos=Vec2(self.rect().center),
                                            rand_f=True):
                    self.game.parts.append(part)

            self.dashing = max(0, self.dashing - 1)

        if self.dashing > self.dashing_max - self.dashing_dur:
            if self.flip:
                self.velocity.x = -8
            else:
                self.velocity.x = 8
            if self.dashing == (self.dashing_max - self.dashing_dur) + 1:
                self.velocity.x *= 0.1

            self.game.parts.append(
                Particle(game=self.game,
                         asset=AssetAnim.PARTICLE_DARK,
                         pos=Vec2(self.rect().center),
                         vel=self.velocity.div(4),
                         rand_f=True))

    def _update_anim(self):
        if not self.y_slide:
            if self.in_air:
                self._set_anim(AssetAnim.PLAYER_JUMP)
            elif self.dashing > self.dashing_max - self.dashing_dur:
                self._set_anim(AssetAnim.PLAYER_SLIDE)
            elif self.velocity_f.x != 0:
                self._set_anim(AssetAnim.PLAYER_RUN)
            else:
                self._set_anim(AssetAnim.PLAYER_IDLE)

    def _norm_vel(self):
        if self.velocity.x > 0:
            self.velocity.x = max(0, self.velocity.x - 0.1)
        else:
            self.velocity.x = min(0, self.velocity.x + 0.1)

    def jump(self):
        if self.y_slide:
            self._y_slide()
        elif self.jumps:
            self._bump(Vec2((0, -3)))

    def _y_slide(self):
        if self.flip and self.velocity_f.x < 0:
            self._bump(Vec2((2.5, -2.5)))
        elif not self.flip and self.velocity_f.x > 0:
            self._bump(Vec2((-2.5, -2.5)))

    def _bump(self, vec=Vec2((0, -2.5))):
        self.in_air = True
        self.jumps = max(0, self.jumps - 1)
        self.velocity.x = vec.x
        self.velocity.y = vec.y

    def dash(self):
        if not self.dashing:
            self.dashing = self.dashing_max
