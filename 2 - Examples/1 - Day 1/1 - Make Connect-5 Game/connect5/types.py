import enum
from collections import namedtuple

# 플레이어 타입(흑돌, 백돌)을 나타내는 클래스
class Player(enum.Enum):
    black = 1
    white = 2

    # 상대 플레이어 타입을 반환하는 메소드
    @property
    def other(self):
        return Player.black if self == Player.white else Player.white

# 바둑판 내 위치(행, 열)를 나타내는 클래스
class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]

# 방향을 나타내는 클래스(열거체)
class Direction(enum.Enum):
    right = 1       # 오른쪽
    down = 2        # 아래
    right_down = 3  # 오른쪽 아래
    left_down = 4   # 왼쪽 아래