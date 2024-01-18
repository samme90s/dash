import pygame

from scripts.assets import AssetAnim
from scripts.utils import Direction, Vector2


class PhysicsEntity:
    def __init__(self, game, asset, size, pos):
        self.game = game
        self.asset = None
        self.size = size
        self.pos = pos.deepcopy()
        self.velocity = Vector2((0, 0))
        self.acceleration = Vector2((0, 0))
        self.collisions = Direction()

        # To account for images with padding.
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_anim(asset)

    def set_anim(self, asset):
        if asset != self.asset:
            self.asset = asset
            self.animation = self.game.assets.get_anim(asset).deepcopy()

    def update(self, tilemap, movement=(0, 0)):
        self.velocity.set(movement)
        self.collisions.reset()
        self._handle_animation()
        self._apply_gravity()
        self._handle_collisions(tilemap)

    def _handle_animation(self):
        if self.velocity.x > 0:
            self.flip = False
        if self.velocity.x < 0:
            self.flip = True

        if self.animation:
            self.animation.update()

    def _apply_gravity(self):
        # Apply gravity, with a terminal velocity.
        # Positive y is down (not like a cartesian plane from math).
        self.acceleration.y = min(5, self.acceleration.y + 0.1)

        if self.collisions.down or self.collisions.up:
            self.acceleration.y = 0

    def _handle_collisions(self, tilemap):
        vector = self.velocity.add(self.acceleration)
        # Usually want to update each axis separately, as below:
        self.pos.x += vector.x
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            # This can be simplified if using FRect (FloatRect) as pos.
            if entity_rect.colliderect(rect):
                if vector.x > 0:
                    entity_rect.right = rect.left
                    self.collisions.right = True
                if vector.x < 0:
                    entity_rect.left = rect.right
                    self.collisions.left = True
                self.pos.x = entity_rect.x

        self.pos.y += vector.y
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if vector.y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions.down = True
                if vector.y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions.up = True
                self.pos.y = entity_rect.y

    def rect(self):
        # This is often updated therefor using a function here is better.
        return pygame.Rect(*self.pos, *self.size)

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  self.pos
                  .sub(offset)
                  .add(self.anim_offset)
                  .tuple())


class Player(PhysicsEntity):
    def __init__(self, game, size, pos):
        super().__init__(game, AssetAnim.PLAYER_IDLE, size, pos)
        self.air_time = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.decide_action()

    def decide_action(self):
        self.air_time += 1
        if self.collisions.down:
            self.air_time = 0

        if self.air_time > 4:
            self.set_anim(AssetAnim.PLAYER_JUMP)
        elif self.velocity.x != 0:
            self.set_anim(AssetAnim.PLAYER_RUN)
        else:
            self.set_anim(AssetAnim.PLAYER_IDLE)

    def jump(self):
        self.acceleration.y = -3
