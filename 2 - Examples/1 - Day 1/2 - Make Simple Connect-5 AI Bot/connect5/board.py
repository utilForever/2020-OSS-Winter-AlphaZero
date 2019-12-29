import copy
from connect5.types import Player, Point, Direction
from connect5 import zobrist

class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = [x[:] for x in [[0] * (self.num_cols + 1)] * (self.num_rows + 1)]
        self._hash = zobrist.EMPTY_BOARD

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

    def zobrist_hash(self):
        return self._hash

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
        self.winner = None

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

    def is_valid_move(self, move):
        return self.board.get(move.point) is 0

    def is_middle(self, r, c, stone_color, direction):
        if direction is Direction.right and self.board.is_on_grid(Point(row=r, col=c-1)):
            if self.board._grid[r][c - 1] is stone_color:
                return False
        if direction is Direction.down and self.board.is_on_grid(Point(row=r-1, col=c)):
            if self.board._grid[r - 1][c] is stone_color:
                return False
        if direction is Direction.right_down and self.board.is_on_grid(Point(row=r-1, col=c-1)):
            if self.board._grid[r - 1][c - 1] is stone_color:
                return False
        if direction is Direction.left_down and self.board.is_on_grid(Point(row=r-1, col=c+1)):
            if self.board._grid[r - 1][c + 1] is stone_color:
                return False
        return True

    def is_connect5(self, r, c, stone_color, direction):
        if not self.is_middle(r, c, stone_color, direction):
            return False
        stones = []
        stones.append(Point(r, c))
        d_row = r
        d_col = c
        if direction is Direction.right:
            d_col += 1
            while self.board.is_on_grid(Point(row=d_row, col=d_col)) and \
                self.board._grid[d_row][d_col] is stone_color:
                stones.append(Point(row=d_row, col=d_col))
                d_col += 1
        elif direction is Direction.down:
            d_row += 1
            while self.board.is_on_grid(Point(row=d_row, col=d_col)) and \
                self.board._grid[d_row][d_col] is stone_color:
                stones.append(Point(row=d_row, col=d_col))
                d_row += 1
        elif direction is Direction.right_down:
            d_row += 1
            d_col += 1
            while self.board.is_on_grid(Point(row=d_row, col=d_col)) and \
                self.board._grid[d_row][d_col] is stone_color:
                stones.append(Point(row=d_row, col=d_col))
                d_row += 1
                d_col += 1              
        elif direction is Direction.left_down:
            d_row += 1
            d_col -= 1
            while self.board.is_on_grid(Point(row=d_row, col=d_col)) and \
                self.board._grid[d_row][d_col] is stone_color:
                stones.append(Point(row=d_row, col=d_col))
                d_row += 1
                d_col -= 1
        if len(stones) is 5:
            return True
        return False      

    def is_over(self):
        is_full = True
        for r in range(1, self.board.num_rows):
            for c in range(1, self.board.num_cols):
                stone_color = self.board._grid[r][c]
                if stone_color is not 0:
                    if stone_color is self.board._grid[r][c + 1]:
                        if self.is_connect5(r, c, stone_color, Direction.right):
                            self.winner = "Black" if stone_color is Player.black else "White"
                            return True
                    if stone_color is self.board._grid[r + 1][c]:
                        if self.is_connect5(r, c, stone_color, Direction.down):
                            self.winner = "Black" if stone_color is Player.black else "White"
                            return True
                    if stone_color is self.board._grid[r + 1][c + 1]:
                        if self.is_connect5(r, c, stone_color, Direction.right_down):
                            self.winner = "Black" if stone_color is Player.black else "White"
                            return True
                    if stone_color is self.board._grid[r + 1][c - 1]:
                        if self.is_connect5(r, c, stone_color, Direction.left_down):
                            self.winner = "Black" if stone_color is Player.black else "White"
                            return True
                else:
                    is_full = False            
        if is_full:
            self.winner = "Draw"
            return True
        else:
            return False