"""
Usage:
    train.py  <data_dir>

Options:
  -h --help     Show this screen.
"""

from networks import Linear
from data_loader import Load_Data

from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from docopt import docopt
import torch
import math
import os

def train(device, model, criterion, optimizer, train_set_loader):
    print(model)
    model.train()
    print(f"Trainig on {device}...")
    for epoch in range(num_epochs):
        losses = []
        for batch_id, (images, other_inputs, labels) in enumerate(train_set_loader):
            print(f"Training batch no:{batch_id}")
            # Get data to cuda
            images = images.to(device=device)
            other_inputs = other_inputs.to(device=device)
            labels = labels.to(device=device).view(-1, 2)
            # Forward
            predictions = model(images, other_inputs)
            loss = criterion(predictions, labels)
            losses.append(loss.item())
            # Backward
            optimizer.zero_grad()
            loss.backward()
            # Gradient Descent Step
            optimizer.step()
        print(f"Cost at epoch {epoch} is {sum(losses)/len(losses)}")

def evaluate(model, test_set_loader):
    model.eval()
    with torch.no_grad():
        for images, other_inputs, labels in test_set_loader:
            images = images.to(device=device)
            other_inputs = other_inputs.to(device=device)
            labels = labels.to(device=device)
        predictions = model(images, other_inputs)
    return criterion(predictions, labels.view(-1, 2)).item()


if __name__ == "__main__":
    args = docopt(__doc__)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    training_date_percentage = 80
    learning_rate = 0.001
    in_channels = 3
    batch_size = 256
    num_epochs = 1

    model = Linear(in_channels=in_channels).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.MSELoss()

    dataset = Load_Data(args["<data_dir>"], transform=transforms.ToTensor())
    train_len = math.floor(len(dataset) * training_date_percentage / 100)
    train_set, test_set = torch.utils.data.random_split(dataset, [train_len, len(dataset)-train_len])
    train_set_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
    test_set_loader = DataLoader(dataset=test_set, batch_size=batch_size, shuffle=True)

    train(device, model, criterion, optimizer, train_set_loader)

    print(f"Cost on test data: {evaluate(model, test_set_loader)}")

    save_filename = os.path.basename(args["<data_dir>"])
    save_path = os.path.join('./models', save_filename)
    torch.save(model.state_dict(), save_path)