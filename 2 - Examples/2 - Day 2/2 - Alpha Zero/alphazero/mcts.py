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

        self.prob = prob
        self.visit_count = 0
        self.win_count = 0

        self.children = {}

    def is_root(self):
        return self.parent is None

    def get_child(self, move):
        return self.children[move]

    def expand(self, probs):
        probs = probs.view(self.state.board.num_rows, self.state.board.num_cols)

        for move in self.state.legal_moves():
            new_state = self.state.apply_move(move)
            prob = probs[move.point.row - 1][move.point.col - 1].item()
            self.children[move] = MCTSNode(new_state, prob, self, move)

    def expanded(self):
        return len(self.children) != 0
    
    def update(self, value):
        self.visit_count += 1
        self.win_count += value
        
    def inject_noise(self, alpha, eps):
        noise = np.random.dirichlet([alpha] * len(self.children))

        total_value = 0
        for i, child in enumerate(self.children.values()):
            child.prob = (1 - eps) * child.prob + eps * noise[i]
            total_value += child.prob
        
        for child in self.children.values():
            child.prob /= total_value

    def pi(self):
        ret = np.zeros((self.state.board.num_rows, self.state.board.num_cols))

        for child in self.children.values():
            ret[child.action.point.row - 1][child.action.point.col - 1] = child.visit_count / self.visit_count

        return ret.reshape(-1)

    @property
    def q_value(self):
        if self.visit_count == 0:
            return 0

        return self.win_count / self.visit_count

class AZAgent(agent.Agent):
    def __init__(self, board_size, state_dict, noise=False, alpha=0.03, eps=0.25, rounds_per_move=1600, puct_init=1.25, puct_base=19652):
        self.network = Network(board_size)
        if USE_CUDA:
            self.network = self.network.cuda()

        self.network.load_state_dict(state_dict)

        self.noise = noise
        self.alpha = alpha
        self.eps = eps

        self.num_rounds = rounds_per_move
        self.puct_init = puct_init
        self.puct_base = puct_base

        self.train_data = []

    def select_move(self, game_state, c_puct=None):
        root = MCTSNode(game_state, 0, None, None)

        for i in range(self.num_rounds):
            node = root
            while node.expanded():
                node = self.select_node(node, c_puct)

            in_data = torch.FloatTensor(preprocess.StateToTensor(node.state))
            if USE_CUDA:
                in_data = in_data.cuda()

            policy, value = self.network(in_data)
            value = value.item()

            if not node.state.is_over():
                # Expand
                policy = F.softmax(policy, dim=1)
                node.expand(policy)

                if self.noise and node.is_root():
                    node.inject_noise(self.alpha, self.eps)

            # Backup
            value = -value
            while node is not None:
                node.update(value)
                node = node.parent

                value = -value

        in_data = preprocess.StateToTensor(game_state)
        self.train_data.append((in_data, root.pi(), game_state.next_player))

        return max(root.children.values(), key=lambda x: x.visit_count).action

    def select_node(self, node, c_puct):
        sqrt_total_visit = math.sqrt(max(node.visit_count, 1))

        def score(move):
            child = node.get_child(move)

            q_value = child.q_value
            puct = math.log((1 + child.visit_count + self.puct_base) / self.puct_base) + self.puct_init if c_puct is None else c_puct
            u_value = puct * child.P * sqrt_total_visit / (1 + child.visit_count)

            return q_value + u_value

        return node.get_child(max(node.children, key=score))
