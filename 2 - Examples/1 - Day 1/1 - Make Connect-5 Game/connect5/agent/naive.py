import random
from connect5.agent.base import Agent
from connect5.board import Move
from connect5.types import Point

# 임의의 위치에 돌을 놓는 에이전트
class RandomBot(Agent):
    # 행동을 선택하는 메소드
    def select_move(self, game_state):
        """Choose a random valid move that preserves our own eyes."""
        candidates = []
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                candidate = Point(row=r, col=c)
                if game_state.is_valid_move(Move.play(candidate)):
                    candidates.append(candidate)
        return Move.play(random.choice(candidates))