from __future__ import print_function
from six.moves import input

from connect5 import board as connect5_board
from connect5 import types
from connect5 import agent
from connect5 import mcts
from connect5.utils import print_board, print_move, point_from_coords

import requests

from connect5_connecter import Connect5Connecter

from alphazero.mcts import AZAgent

import torch
import time
import sys


BOARD_SIZE = 7

# 서버 주소입니다.
HOST = 'http://18.189.17.31:80/'


def main():
    game = connect5_board.GameState.new_game(BOARD_SIZE)
    # 사용하고 싶은 bot을 넣어주세요.
    bot = AZAgent(BOARD_SIZE, torch.load(sys.argv[1]), rounds_per_move=400)

    # bot의 name을 정합니다. 다른 팀과 중복되면 안됩니다.
    name = 'c301-bot'

    # 서버와의 통신에 사용되는 Connect5Connecter 클래스 객체를 만듭니다.
    # connecter 관련 부분은 수정하지 말아주세요. 서버랑 통신할 때 문제가 생깁니다.
    connecter = Connect5Connecter(HOST, name)

    # 서버에서 자기 차례에 state를 가져옵니다.
    state = connecter.get_state()
    # 서버에서 정해준 bot의 color로 is_my_turn을 결정합니다.
    if state['color'] == 'black':
        print("I'm black.")
        is_my_turn = True
    elif state['color'] == 'white':
        print("I'm white.")
        is_my_turn = False
    else:
        print('invalid color')

    while not game.is_over():
        # 서버에서 자기 차례에 state를 가져옵니다.
        state = connecter.get_state()
        # bot의 차례라면 send_action으로 서버에 bot의 action을 전송합니다.
        # 아니면 서버에서 oppnent의 action을 가져와 game에 적용합니다.
        if is_my_turn:
            move = bot.select_move(game)
            game = game.apply_move(move)
            connecter.send_action(move.point.col, move.point.row)
        else:
            move = connect5_board.Move.play(types.Point(
                row=int(state['opponent_action']['y']), col=int(state['opponent_action']['x'])))
            game = game.apply_move(move)
        print_board(game.board)
        # is_my_turn을 뒤집습니다.
        is_my_turn = not is_my_turn

    # 누가 이겼는지 서버에 알려줍니다.
    connecter.notice_winner(game.winner)


if __name__ == '__main__':
    main()
