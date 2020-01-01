from six.moves import input

from connect5 import board as connect5_board
from connect5 import types
from connect5 import mcts
from connect5.utils import print_board, print_move, point_from_coords

BOARD_SIZE = 5

def main():
    game = connect5_board.GameState.new_game(BOARD_SIZE)
    bot = mcts.MCTSAgent(500, temperature=1.4)

    while not game.is_over():
        print_board(game.board)
        if game.next_player == types.Player.black:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())
            move = connect5_board.Move.play(point)
        else:
            move = bot.select_move(game)
        print_move(game.next_player, move)
        game = game.apply_move(move)

if __name__ == '__main__':
    main()