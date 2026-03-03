"""
Audio Model Training Pipeline
-----------------------------
"""

import torch
from torch import nn, optim
from torch.utils.data import DataLoader

class AudioModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.net(x)

def train():
        model = AudioModel()
        optimizer = optim.Adam(model.parameters(), lr=1e-4)
        criterion = nn.BCEWithLogitsLoss()

        # dataset & dataloader placeholder
        # for epoch in epochs:
        #   forward → loss → backward → step

        torch.save(model.state_dict(), "models/audio_model.pt")
