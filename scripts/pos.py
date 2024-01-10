class Pos:
    def __init__(self, tuple: tuple):
        self.tuple = tuple

    def json(self):
        return str(self.tuple[0]) + ';' + str(self.tuple[1])
