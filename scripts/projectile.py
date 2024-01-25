from scripts.utils import Vec2


class Proj:
    def __init__(self, pos=Vec2((0, 0)), vel=Vec2((0, 0))):
        self.pos = pos.deepcopy()
        self.vel = vel.deepcopy()
        self.timer = 0
