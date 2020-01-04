import math
import numpy as np

import torch
import torch.nn.functional as F

from alphazero import preprocess
from alphazero.network import Network

from connect5 import agent
from connect5.types import Player
from connect5.utils import coords_from_point

USE_CUDA = torch.cuda.is_available()

class MCTSNode(object):
    def __init__(self, state, prob, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

        self.P = prob
        self.N = 0
        self.W = 0

        self.children = {}

    def has_child(self, move):
        return move in self.children

    def get_child(self, move):
        return self.children[move]

    def expand(self, probs):
        probs = probs.view(self.state.board.num_rows, self.state.board.num_cols)

        for move in self.state.legal_moves():
            new_state = self.state.apply_move(move)
            prob = prob[move.point.row - 1][move.point.col - 1]
            self.children[move] = MCTSNode(new_state, prob, self, move)
    
    def update(self, value):
        self.N += 1
        self.W += value

    def pi(self):
        ret = np.zeros((self.state.board.num_rows, self.state.board.num_cols))

        for child in self.children:
            ret[child.action.point.row - 1][child.action.point.col - 1] = child.N / self.N

        return ret

    @property
    def Q(self):
        if self.N == 0:
            return 0

        return self.W / self.N

class AZAgent(agent.Agent):
    def __init__(self, state_dict, noise=False, rounds_per_move=1600, puct_init=1.25, puct_base=19652):
        self.network = Network()
        self.network.load_state_dict(state_dict)

        self.noise = noise
        self.num_rounds = rounds_per_move
        self.puct_init = puct_init
        self.puct_base = puct_base

        self.train_data = []

    def select_move(self, game_state):
        root = MCTSNode(game_state, 0, None, None)

        for i in range(self.num_rounds):
            node = root
            next_move = self.select_node(node)
            while node.has_child(next_move):
                node = node.get_child(next_move)
                next_move = self.select_node(node)

            next_state = node.state.apply_move(next_move)

            in_data = torch.FloatTensor(preprocess.StateToTensor(next_state))
            if USE_CUDA:
                in_data = in_data.cuda()

            policy, value = self.network(in_data)
            
            # Expand
            policy = F.softmax(policy, dim=1)
            node.expand(policy)

            # Backup
            value = -value
            while node is not None:
                node.update(value)
                node = node.parent

                value = -value

        in_data = preprocess.StateToTensor(game_state)
        self.train_data.append((in_data, root.pi(), game_state.next_player))

        return max(root.children, key=lambda x: x.N).action

    def select_node(self, node):
        sqrt_total_visit = math.sqrt(node.N)

        def score(child):
            Q = child.Q
            puct = math.log((1 + child.N + self.puct_base) / self.puct_base) + self.puct_init
            U = puct * child.P * sqrt_total_visit / (1 + child.N)

            return Q + U

        return max(node.children, key=score).action
