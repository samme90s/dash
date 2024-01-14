import pygame

from scripts.assets import AssetAnim


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type.upper()
        self.pos = pos.copy()
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False,
                           'left': False,
                           'down': False,
                           'right': False}

        # To account for images with padding.
        self.anim_offset = (-3, -3)
        self.flip = False
        self.action = ''
        self.set_action(AssetAnim[f'{self.type}_IDLE'])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets.get_anim(action).copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False,
                           'left': False,
                           'down': False,
                           'right': False}

        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

        self.handle_animation(movement)
        self.handle_collisions(tilemap, frame_movement)
        self.apply_gravity()

    def handle_animation(self, movement):
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        if self.animation:
            self.animation.update()

    def handle_collisions(self, tilemap, frame_movement):
        # Usually want to update each axis separately, as below:
        self.pos.x += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            # This can be simplified if using FRect (FloatRect) as pos.
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos.x = entity_rect.x

        self.pos.y += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos.y = entity_rect.y

    def apply_gravity(self):
        # Apply gravity, with a terminal velocity.
        # Positive y is down (not like a cartesian plane from math).
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

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
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.decide_action(movement)

    def decide_action(self, movement):
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0

        if self.air_time > 4:
            self.set_action(AssetAnim.PLAYER_JUMP)
        elif movement[0] != 0:
            self.set_action(AssetAnim.PLAYER_RUN)
        else:
            self.set_action(AssetAnim.PLAYER_IDLE)

    def jump(self):
        self.velocity[1] = -3
