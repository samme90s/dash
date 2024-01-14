class Tile:
    def __init__(self, type, variant, pos):
        self.type = type
        self.variant = variant
        self.pos = pos.copy()

    def to_dict(self):
        return {
            'type': self.type.name,
            'variant': self.variant,
            'pos': self.pos.tuple(),
        }
