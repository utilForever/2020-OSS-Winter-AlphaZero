import copy
from connect5.types import Player

class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = [x[:] for x in [[0] * (self.num_cols + 1)] * (self.num_rows + 1)]

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid[point.row][point.col] is 0
        self._grid[point.row][point.col] = player

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        stone_color = self._grid[point.row][point.col]
        return stone_color

class Move:
    def __init__(self, point=None):
        assert (point is not None)
        self.point = point

    @classmethod
    def play(cls, point):
        return Move(point=point)

    def __str__(self):
        return '(r %d, c %d)' % (self.point.row, self.point.col)

class GameState:
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(previous.previous_states |
            {(previous.next_player, previous.board.zobrist_hash())})
        self.last_move = move

    def apply_move(self, move):
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(self.next_player, move.point)
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)