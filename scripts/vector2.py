class Vector2:
    def __init__(self, pos):
        [self.x, self.y] = pos

    def __iter__(self):
        yield self.x
        yield self.y

    def multiply(self, scalar):
        return Vector2((self.x * scalar, self.y * scalar))

    def sub(self, offset):
        return Vector2((self.x - offset[0], self.y - offset[1]))

    def mod(self, offset):
        return Vector2((self.x % offset[0], self.y % offset[1]))

    def tuple(self):
        return (self.x, self.y)

    def json(self):
        return str(self.x) + ';' + str(self.y)
