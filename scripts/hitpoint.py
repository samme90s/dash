class Hitpoint:
    def __init__(self, total):
        self.total = total
        self.actual = total

    def is_dead(self):
        return self.actual <= 0

    def reduce(self, dam):
        self.actual -= dam
        if self.actual < 0:
            self.actual = 0
