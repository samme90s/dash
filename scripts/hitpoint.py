class Hitpoint:
    def __init__(self, total=1):
        self.total = total
        self.actual = total

    def is_dead(self):
        return self.actual <= 0

    def reduce(self, dam=1):
        self.actual -= dam
        if self.actual < 0:
            self.actual = 0
