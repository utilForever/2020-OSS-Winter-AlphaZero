import multiprocessing as mp
import os
import time

import numpy as np
import torch
import torch.nn.functional as F
from tensorboardX import SummaryWriter
from torch import optim

from alphazero import preprocess
from alphazero.mcts import AZAgent
from alphazero.network import Network
from alphazero.replaybuffer import ReplayBuffer
from connect5 import agent
from connect5 import board as connect5_board
from connect5 import types

USE_CUDA = torch.cuda.is_available()

# 학습 설정값을 저장하는 딕셔너리
TRAINING_CONFIG = {
    'BOARD_SIZE': 7,

    'LEARNING_RATE': 1e-2,
    'WEIGHT_DECAY': 1e-4,

    'ROUNDS_PER_MOVE': 800,
    'PUCT': 1.25,
    'PUCT_INIT': 1.25,
    'PUCT_BASE': 19652,

    'MCTS_NOISE': True,
    'MCTS_ALPHA': 0.03,
    'MCTS_EPS': 0.25,

    'SELFPLAY_WORKERS': 12,
    'START_TRAINING': 1280,
    'EPOCH': 1,
    'BATCH_SIZE': 128,
    'CAPACITY': 10000,

    'LOAD_CHECKPOINT': 0
}

buffer = ReplayBuffer(TRAINING_CONFIG['CAPACITY'])

target_network = Network(TRAINING_CONFIG['BOARD_SIZE'])

if USE_CUDA:
    target_network = target_network.cuda()

if TRAINING_CONFIG['LOAD_CHECKPOINT'] != 0:
    target_network.load_state_dict(torch.load(f'models/checkpoint-{TRAINING_CONFIG["LOAD_CHECKPOINT"]}.bin'))

# 자가 대국을 하는 작업자
def selfplay_worker(queue):
    while True:
        game = connect5_board.GameState.new_game(TRAINING_CONFIG['BOARD_SIZE'])
        agent = AZAgent(TRAINING_CONFIG['BOARD_SIZE'], target_network.state_dict(), \
            TRAINING_CONFIG['MCTS_NOISE'], TRAINING_CONFIG['MCTS_ALPHA'], TRAINING_CONFIG['MCTS_EPS'], \
            TRAINING_CONFIG['ROUNDS_PER_MOVE'], TRAINING_CONFIG['PUCT_INIT'], TRAINING_CONFIG['PUCT_BASE'])

        while not game.is_over():
            move = agent.select_move(game, TRAINING_CONFIG['PUCT'])
            game = game.apply_move(move)

        queue.put((game.winner, agent.train_data))

# 프로그램의 메인 함수
def main():
    step = TRAINING_CONFIG['LOAD_CHECKPOINT']
    num_game = 0

    manager = mp.Manager()
    queue = manager.Queue()

    writer = SummaryWriter()

    opt = optim.SGD(target_network.parameters(), lr=TRAINING_CONFIG['LEARNING_RATE'], weight_decay=TRAINING_CONFIG['WEIGHT_DECAY'], momentum=0.9)

    if not os.path.exists('models'):
        os.mkdir('models')

    # 작업자를 만드는 부분
    workers = []
    for _ in range(TRAINING_CONFIG['SELFPLAY_WORKERS']):
        p = mp.Process(target=selfplay_worker, args=(queue,))
        p.daemon = True
        p.start()

        workers.append(p)

    # 학습을 돌리는 코드
    while True:
        try:
            winner, result = queue.get()
            buffer.push(winner, result)
            
            num_game += 1
            print(f'selfplay game #{num_game}')

            if len(buffer) < TRAINING_CONFIG['START_TRAINING']:
                continue

            step += 1
            print(f'start training #{step}')

            total_pi = 0
            total_v = 0
            total_loss = 0

            for _ in range(TRAINING_CONFIG['EPOCH']):
                states, pis, values = buffer.sample(TRAINING_CONFIG['BATCH_SIZE'])
                if USE_CUDA:
                    states, pis, values = states.cuda(), pis.cuda(), values.cuda()

                opt.zero_grad()
                out_pi, out_v = target_network(states)
                out_pi = F.log_softmax(out_pi, dim=1)

                loss_pi = -(out_pi * pis).sum(dim=1).mean()
                loss_v = F.mse_loss(out_v, values)
                
                loss = loss_pi + loss_v
                loss.backward()
                opt.step()

                total_pi = loss_pi.item()
                total_v = loss_v.item()
                total_loss = loss.item()

            buffer.clear_half()
            torch.save(target_network.state_dict(), f'models/checkpoint-{step}.bin')

            writer.add_scalar('train total loss', total_loss / TRAINING_CONFIG['EPOCH'], step)
            writer.add_scalar('train pi loss', total_pi / TRAINING_CONFIG['EPOCH'], step)
            writer.add_scalar('train value loss', total_v / TRAINING_CONFIG['EPOCH'], step)
        except KeyboardInterrupt:
            print('Stopping training...')

            for worker in workers:
                worker.terminate()
            break

        except Exception as e:
            print('Exception', e)
            continue

if __name__ == '__main__':
    mp.set_start_method('spawn')
    main()
