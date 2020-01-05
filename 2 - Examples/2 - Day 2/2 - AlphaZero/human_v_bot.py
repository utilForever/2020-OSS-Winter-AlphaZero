from __future__ import print_function
from alphazero.mcts import AZAgent
from connect5 import board as connect5_board
from connect5 import types
from connect5.utils import print_board, print_move, point_from_coords
from six.moves import input

import torch
import sys

def main():
    board_size = 6
    game = connect5_board.GameState.new_game(board_size)
    bot = AZAgent(board_size, torch.load(sys.argv[1]), rounds_per_move=400)

    while not game.is_over():
        print(chr(27) + "[2J")
        print_board(game.board)
        if game.next_player == types.Player.black:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())
            move = connect5_board.Move.play(point)
        else:
            move = bot.select_move(game)
        print_move(game.next_player, move)
        game = game.apply_move(move)

    print(chr(27) + "[2J")
    print_board(game.board)

    if game.winner is "Draw":
        print("Draw!")
    else:
        print("Winner is %s!" % game.winner)

if __name__ == '__main__':
    main()