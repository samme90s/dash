class Tile:
    def __init__(self, type, variant, pos):
        self.type = type
        self.variant = variant
        self.pos = pos.deepcopy()

    def deepcopy(self):
        return Tile(self.type, self.variant, self.pos)

    def to_dict(self):
        return {
            'type': self.type.name,
            'variant': self.variant,
            'pos': self.pos.tuple(),
        }
