import numpy as np 

from connect5.types import Player, Point

PAST_MOVES = 4
TENSOR_DIM = PAST_MOVES * 2 + 1

# 오목판을 Tensor로 만들어주는 함수
def StateToTensor(state):
    rows, cols = state.board.num_rows, state.board.num_cols

    data = np.zeros((TENSOR_DIM, rows, cols))
    
    data[TENSOR_DIM - 1, :, :] = 1 if state.next_player == Player.black else 0

    current, opponent = state.next_player, state.next_player.other

    for move in range(min(PAST_MOVES, len(state.previous_states))):
        for x in range(cols):
            for y in range(rows):
                point = Point(col=x+1, row=y+1)

                if state.board.get(point) == current:
                    data[2 * move + 0, y, x] = 1
                elif state.board.get(point) == opponent:
                    data[2 * move + 1, y, x] = 1

        state = state.previous_state

    return data.reshape(1, TENSOR_DIM, rows, cols)
