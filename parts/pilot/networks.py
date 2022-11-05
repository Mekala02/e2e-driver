import torch
import torch.nn as nn
import torch.nn.functional as F


class Linear(nn.Module):
    def __init__(self, in_channels=3):
        super(Linear, self).__init__()
        self.drop = nn.Dropout(p=0.0)
        self.flatten = nn.Flatten()
        self.conv1 = nn.Conv2d(in_channels=in_channels, out_channels =24, kernel_size =(5, 5), stride=(2, 2))
        self.conv2 = nn.Conv2d(in_channels=24, out_channels=32, kernel_size=(5, 5), stride=(2, 2))
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(5, 5), stride=(2, 2))
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1))
        self.conv5 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1))
        self.fc1 = nn.Linear(6656, 100)
        self.fc2 = nn.Linear(100, 50)

        self.out1 = nn.Linear(50, 1)
        self.out2 = nn.Linear(50, 1)

    def forward(self, images):
        x = F.relu(self.conv1(images))
        x = self.drop(x)
        x = F.relu(self.conv2(x))
        x = self.drop(x)
        x = F.relu(self.conv3(x))
        x = self.drop(x)
        x = F.relu(self.conv4(x))
        x = self.drop(x)
        x = F.relu(self.conv5(x))
        x = self.drop(x)
        x = self.flatten(x)

        x = F.relu(self.fc1(x))
        x = self.drop(x)
        x = F.relu(self.fc2(x))
        x = self.drop(x)

        steering = self.out1(x)
        throttle = self.out2(x)

        return steering, throttle

class Linear_With_Others(nn.Module):
    def __init__(self, in_channels=3):
        super(Linear_With_Others, self).__init__()
        self.drop = nn.Dropout(p=0.0)
        self.flatten = nn.Flatten()
        self.conv1 = nn.Conv2d(in_channels=in_channels, out_channels =24, kernel_size =(5, 5), stride=(2, 2))
        self.conv2 = nn.Conv2d(in_channels=24, out_channels=32, kernel_size=(5, 5), stride=(2, 2))
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(5, 5), stride=(2, 2))
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1))
        self.conv5 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1))
        self.fc1 = nn.Linear(6656, 100)
        self.fc2 = nn.Linear(100, 50)

        self.ofc1 = nn.Linear(7, 50)
        self.ofc2 = nn.Linear(50, 40)
        self.ofc3 = nn.Linear(40, 30)

        self.cfc1 = nn.Linear(80, 60)
        self.cfc2 = nn.Linear(60, 50)

        self.out1 = nn.Linear(50, 1)
        self.out2 = nn.Linear(50, 1)

    def forward(self, images, other_inputs):
        x = F.relu(self.conv1(images))
        x = self.drop(x)
        x = F.relu(self.conv2(x))
        x = self.drop(x)
        x = F.relu(self.conv3(x))
        x = self.drop(x)
        x = F.relu(self.conv4(x))
        x = self.drop(x)
        x = F.relu(self.conv5(x))
        x = self.drop(x)
        x = self.flatten(x)

        x = F.relu(self.fc1(x))
        x = self.drop(x)
        x = F.relu(self.fc2(x))
        x = self.drop(x)
        
        y = self.flatten(other_inputs)
        y = F.relu(self.ofc1(y))
        y = F.relu(self.ofc2(y))
        y = F.relu(self.ofc3(y))

        z = torch.cat((x, y), 1)
        z = F.relu(self.cfc1(z))
        z = self.drop(z)
        z = F.relu(self.cfc2(z))
        z = self.drop(z)

        steering = self.out1(z)
        throttle = self.out2(z)

        return steering, throttle