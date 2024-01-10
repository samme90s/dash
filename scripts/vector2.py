class Vector2:
    def __init__(self, pos):
        [self.x, self.y] = pos

    def multiply(self, scalar):
        return Vector2((self.x * scalar, self.y * scalar))

    # Update the method name to "subtract"?
    def offset_inverse(self, offset):
        return Vector2((self.x - offset[0], self.y - offset[1]))

    def tuple(self):
        return (self.x, self.y)

    def json(self):
        return str(self.x) + ';' + str(self.y)
