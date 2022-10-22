import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class Linear(nn.Module):
    def __init__(self, in_channels=3):
        super(Linear, self).__init__()
        self.relu = nn.ReLU()
        self.drop = nn.Dropout(p=0.2)
        self.flatten = nn.Flatten()
        self.conv1 = nn.Conv2d(in_channels=in_channels, out_channels =24, kernel_size =(5, 5), stride=(2, 2), padding=(1, 1))
        self.conv2 = nn.Conv2d(in_channels=24, out_channels=32, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(5, 5), stride=(2, 2), padding=(3, 3))
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1), padding=(4, 4))
        self.conv5 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1), padding=(5, 5))
        self.fc1 = nn.LazyLinear(100)

        self.ofc1 = nn.LazyLinear(40)
        self.ofc2 = nn.Linear(40, 30)
        self.ofc3 = nn.Linear(30, 20)

        self.cfc1 = nn.LazyLinear(100)
        self.cfc2 = nn.Linear(100, 50)

        self.out1 = nn.Linear(50, 1)
        self.out2 = nn.Linear(50, 1)

    def forward(self, images, other_inputs):
        x = self.relu(self.conv1(images))
        x = self.drop(x)
        x = self.relu(self.conv2(x))
        x = self.drop(x)
        x = self.relu(self.conv3(x))
        x = self.drop(x)
        x = self.relu(self.conv4(x))
        x = self.drop(x)
        x = self.relu(self.conv5(x))
        x = self.drop(x)
        x = self.flatten(x)

        x = self.relu(self.fc1(x))
        x = self.drop(x)
        
        y = self.flatten(other_inputs)
        y = self.relu(self.ofc1(y))
        y = self.relu(self.ofc2(y))
        y = self.relu(self.ofc3(y))

        z = torch.cat((x, y), 1)
        z = self.relu(self.cfc1(z))
        z = self.drop(z)
        z = self.relu(self.cfc2(z))
        z = self.drop(z)

        angle = self.out1(z)
        throttle = self.out2(z)

        return torch.cat((angle, throttle), 1)