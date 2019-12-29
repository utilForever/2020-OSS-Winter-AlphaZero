from __future__ import print_function
from connect5 import agent
from connect5 import board as connect5_board
from connect5 import types
from connect5.utils import print_board, print_move
import time

def main():
    board_size = 9
    game = connect5_board.GameState.new_game(board_size)
    bots = {
        types.Player.black: agent.naive.RandomBot(),
        types.Player.white: agent.naive.RandomBot(),
    }

    while not game.is_over():
        time.sleep(0.3)

        print(chr(27) + "[2J")
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)

    print(chr(27) + "[2J")
    print_board(game.board)
    
    print("Winner is %s!" % game.winner)

if __name__ == '__main__':
    main()