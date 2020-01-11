import numpy as np
import torch

from connect5.types import Player

# 자가 대국의 결과를 저장하는 버퍼
class ReplayBuffer:
    # 초기화 메소드
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []

    # 버퍼를 전부 비우는 메소드
    def clear(self):
        self.buffer = []

    # 버퍼의 절반만 비우는 메소드
    def clear_half(self):
        length = len(self.buffer) // 2

        self.buffer = self.buffer[length:]

    # 버퍼에 데이터를 넣는 메소드
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

    # 버퍼에서 무작위로 샘플을 추출하는 메소드
    def sample(self, size):
        indicies = np.random.choice(len(self.buffer), size, replace=False)

        states, pis, values = [], [], []
        for i in indicies:
            state, pi, value = self.buffer[i]

            states.append(state)
            pis.append(pi)
            values.append(value)

        return torch.FloatTensor(np.concatenate(states, axis=0)), torch.FloatTensor(pis).view(size, -1), torch.FloatTensor(values).view(size, 1)                                                                                      

    # 버퍼에 들어있는 샘플의 개수를 구하는 메소드
    def __len__(self):
        return len(self.buffer)
