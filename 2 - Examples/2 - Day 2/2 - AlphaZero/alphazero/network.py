import torch
from torch import nn, optim

from alphazero import preprocess

FILTERS = 64

# 3차원 Tensor를 1차원으로 만드는 클래스
class Flatten(nn.Module):
    # 초기화 메소드
    def __init__(self):
        nn.Module.__init__(self)

    # 연산하는 메소드
    def forward(self, x):
        return x.view(x.size(0), -1)

# 신경망 클래스
class Network(nn.Module):
    # 초기화 메소드
    def __init__(self, board_size):
        nn.Module.__init__(self)

        self.feature_extraction = nn.Sequential(
            nn.Conv2d(preprocess.TENSOR_DIM, FILTERS, 3, padding=1),
            nn.BatchNorm2d(FILTERS),
            nn.ReLU(inplace=True),
            nn.Conv2d(FILTERS, FILTERS, 3, padding=1),
            nn.BatchNorm2d(FILTERS),
            nn.ReLU(inplace=True),
            nn.Conv2d(FILTERS, FILTERS, 3, padding=1),
            nn.BatchNorm2d(FILTERS),
            nn.ReLU(inplace=True),
        )

        self.policy_head = nn.Sequential(
            nn.Conv2d(FILTERS, 2, 1, padding=0),
            nn.BatchNorm2d(2),
            nn.ReLU(inplace=True),
            Flatten(),
            nn.Linear(2 * (board_size ** 2), board_size ** 2)
        )

        self.value_head = nn.Sequential(
            nn.Conv2d(FILTERS, 1, 1, padding=0),
            nn.BatchNorm2d(1),
            nn.ReLU(inplace=True),
            Flatten(),
            nn.Linear(board_size ** 2, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 1),
            nn.Tanh()
        )
    
    # 연산하는 메소드
    def forward(self, x):
        x = self.feature_extraction(x)

        return self.policy_head(x), self.value_head(x)
