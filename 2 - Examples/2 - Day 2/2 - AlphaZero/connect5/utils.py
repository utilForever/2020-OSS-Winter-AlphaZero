from connect5 import types

# 열을 출력하기 위한 문자열
COLS = 'ABCDEFGHJKLMNOPQRST'
# 열거체 값에 따라 돌을 출력하기 위한 문자열
STONE_TO_CHAR = {
    0: ' . ',
    types.Player.black: ' x ',
    types.Player.white: ' o ',
}

# 돌을 어디에 착수했는지 출력하는 함수
def print_move(player, move):
    move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)
    print('%s %s' % (player, move_str))

# 바둑판을 출력하는 함수
def print_board(board):
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(types.Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.num_cols]))

# 좌표를 바둑판 내 위치로 변환하는 함수
def point_from_coords(coords):
    col = COLS.index(coords[0]) + 1
    row = int(coords[1:])
    return types.Point(row=row, col=col)

# 바둑판 내 위치를 좌표로 변환하는 함수
def coords_from_point(point):
    return '%s%d' % (
        COLS[point.col - 1],
        point.row
    )