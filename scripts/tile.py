class Tile:
    def __init__(self, type, var, pos):
        self.type = type
        self.var = var
        self.pos = pos.deepcopy()

    def deepcopy(self):
        return Tile(self.type, self.var, self.pos)

    def to_dict(self):
        return {
            'type': self.type.name,
            'var': self.var,
            'pos': self.pos.tuple(),
        }
