class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = [x[:] for x in [[0] * self.num_cols] * self.num_rows]

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        stone = self._grid[point.row][point.col]
        if stone is None:
            return None
        return stone.color

class Move:
    def __init__(self, point=None):
        assert (point is not None)
        self.point = point

    @classmethod
    def play(cls, point):
        return Move(point=point)

    def __str__(self):
        return '(r %d, c %d)' % (self.point.row, self.point.col)