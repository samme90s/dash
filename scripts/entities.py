class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = pos
        # Possibly use pygame.Vector2 instead?
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]

    def update(self, movement=(0, 0)):
        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

        # Apply gravity, with a terminal velocity.
        # Positive y is down (not like a cartesian plane from math).
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Usually want to update each axis separately, as below:
        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]

    def render(self, surf):
        surf.blit(self.game.assets['player'], self.pos)
