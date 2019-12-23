import random
from agent.base import Agent

class RandomBot(Agent):
    def select_move(self, game_state):
        """Choose a random valid move that preserves our own eyes."""
        candidates = []
        for r range(1, game_state.board.num_rows + 1):
            for c range(1, game_state.board.num_cols + 1):
                candidate = Point(row=r, col=c)
                if game_state.is_valid_move(Move.play(candidate)):
                    candidates.append(candidate)
        return Move.play(random.choice(candidates))