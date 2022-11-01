"""
Usage:
    train.py  <data_dir>

Options:
  -h --help     Show this screen.
"""

from networks import Linear
from data_loader import Load_Data

from torch.utils.data import DataLoader
from docopt import docopt
import torch
import math
import os

def train(device, model, criterion, optimizer, train_set_loader, test_set_loader=None):
    # torch.autograd.set_detect_anomaly(True)
    print(model)
    print(f"Trainig on {device}...")
    for epoch in range(1, num_epochs+1):
        model.train()
        steering_losses = []
        throttle_losses = []
        for batch_id, (images, other_inputs, steering_labels, throttle_labels) in enumerate(train_set_loader, 1):
            print(f"Training batch no:{batch_id}")
            optimizer.zero_grad()
            # Get data to cuda
            images = images.to(device=device)
            other_inputs = other_inputs.to(device=device)
            steering_labels = steering_labels.to(device=device)
            throttle_labels = throttle_labels.to(device=device)
            # Forward
            steering_prediction, throttle_prediction = model(images, other_inputs)
            steering_loss = criterion(steering_prediction, steering_labels)
            steering_losses.append(steering_loss.item())
            throttle_loss = criterion(throttle_prediction, throttle_labels)
            throttle_losses.append(throttle_loss.item())
            loss = steering_loss + throttle_loss
            # Backward
            loss.backward()
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5)
            # Gradient Descent Step
            optimizer.step()
        print(f"Epoch{epoch}/{num_epochs}")
        loss_string = f"Steering Loss: {(sum(steering_losses)/len(steering_losses)):.2e}, Throttle Loss: {(sum(throttle_losses)/len(throttle_losses)):.2e}"
        if test_set_loader:
            steering_loss, throttle_loss = evaluate(model, test_set_loader)
            val_loss_string = f"Steering Val Loss: {steering_loss:.2e}, Throttle Val Loss: {throttle_loss:.2e}"
            print(loss_string + " - " + val_loss_string)
        else:
            print(loss_string)

def evaluate(model, test_set_loader):
    model.eval()
    with torch.no_grad():
        for images, other_inputs, steering_labels, throttle_labels in test_set_loader:
            images = images.to(device=device)
            other_inputs = other_inputs.to(device=device)
            steering_labels = steering_labels.to(device=device)
            throttle_labels = throttle_labels.to(device=device)
        steering_prediction, throttle_prediction = model(images, other_inputs)
    return criterion(steering_prediction, steering_labels), criterion(throttle_prediction, throttle_labels)


if __name__ == "__main__":
    args = docopt(__doc__)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_depth_input = False
    training_date_percentage = 80
    learning_rate = 0.0001
    if use_depth_input:
        in_channels = 4
    else:
        in_channels = 3
    batch_size = 256
    num_epochs = 1

    model = Linear(in_channels=in_channels).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.MSELoss()

    dataset = Load_Data(args["<data_dir>"], use_depth_input=use_depth_input)
    train_len = math.floor(len(dataset) * training_date_percentage / 100)
    train_set, test_set = torch.utils.data.random_split(dataset, [train_len, len(dataset)-train_len])
    train_set_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
    test_set_loader = DataLoader(dataset=test_set, batch_size=batch_size, shuffle=True)

    train(device, model, criterion, optimizer, train_set_loader, test_set_loader)

    # Saving the model
    save_filename = os.path.basename(args["<data_dir>"])
    save_file_path = os.path.join('./models', save_filename+".pt")
    torch.save(model.state_dict(), save_file_path)