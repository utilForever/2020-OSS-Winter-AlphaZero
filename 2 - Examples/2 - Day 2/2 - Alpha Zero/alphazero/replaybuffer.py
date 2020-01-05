import torch
import numpy as np

from connect5.types import Player

class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []

    def clear(self):
        self.buffer = []

    def clear_half(self):
        length = len(self.buffer) // 2

        self.buffer = self.buffer[length:]

    def push(self, winner, data):
        if winner is 'Draw':
            winner = None
        else:
            winner = Player.black if winner == 'Black' else Player.white

        for state, pi, color in data:
            if winner is None:
                value = 0
            else:
                value = 1 if winner == color else -1

            self.buffer.append((state, pi, value))

        if len(self.buffer) > self.capacity:
            self.buffer = self.buffer[-self.capacity:]

    def sample(self, size):
        indicies = np.random.choice(len(self.buffer), size, replace=False)

        states, pis, values = [], [], []
        for i in indicies:
            state, pi, value = self.buffer[i]

            states.append(state)
            pis.append(pi)
            values.append(value)

        return torch.FloatTensor(np.concatenate(states, axis=0)), torch.FloatTensor(pis).view(size, -1), torch.FloatTensor(values).view(size, 1)                                                                                      

    def __len__(self):
        return len(self.buffer)