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
from tqdm import tqdm
import sys
import torch
import math
import os

def train(device, model, criterion, optimizer, train_set_loader, test_set_loader=None, use_other_inputs=False):
    # torch.autograd.set_detect_anomaly(True)
    nu_of_batches = len(train_set_loader)
    # print(model)
    print(f"Trainig on {device}...")
    for epoch in range(1, num_epochs+1):
        model.train()
        steering_losses = []
        throttle_losses = []
        pbar = tqdm(train_set_loader, desc=f"Epoch: {epoch}", file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}')
        for batch_no, data in enumerate(pbar, 1):
            optimizer.zero_grad()
            if use_other_inputs:
                images, other_inputs, steering_labels, throttle_labels = data
                other_inputs = other_inputs.to(device=device)
            else:
                images, steering_labels, throttle_labels = data
            # Get data to cuda
            images = images.to(device=device)
            steering_labels = steering_labels.to(device=device)
            throttle_labels = throttle_labels.to(device=device)
            # Forward
            if use_other_inputs:
                steering_prediction, throttle_prediction = model(images, other_inputs)
            else:
                steering_prediction, throttle_prediction = model(images)
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
            print(f"\nBatch[{batch_no}/{nu_of_batches}] Steering Loss: {steering_loss:.2e}, Throttle Loss: {throttle_loss:.2e}")
        loss_string = f"For Epoch {epoch} --> Steering Loss: {(sum(steering_losses)/len(steering_losses)):.2e}, Throttle Loss: {(sum(throttle_losses)/len(throttle_losses)):.2e}"
        if test_set_loader:
            print("Evaluating on test set ...")
            steering_loss, throttle_loss = evaluate(model, test_set_loader)
            val_loss_string = f"Steering Val Loss: {steering_loss:.2e}, Throttle Val Loss: {throttle_loss:.2e}"
            print(loss_string + " - " + val_loss_string)
        else:
            print(loss_string)
        save_model()

def evaluate(model, test_set_loader, use_other_inputs=False):
    model.eval()
    with torch.no_grad():
        for data in tqdm(test_set_loader, file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}'):
            if use_other_inputs:
                images, other_inputs, steering_labels, throttle_labels = data
                other_inputs = other_inputs.to(device=device)
            else:
                images, steering_labels, throttle_labels = data
            images = images.to(device=device)
            steering_labels = steering_labels.to(device=device)
            throttle_labels = throttle_labels.to(device=device)
        if use_other_inputs:  
            steering_prediction, throttle_prediction = model(images, other_inputs)
        else:
            steering_prediction, throttle_prediction = model(images)
    return criterion(steering_prediction, steering_labels), criterion(throttle_prediction, throttle_labels)

def save_model():
    model_save_path = os.path.join('./models', "model.pt")
    jit_model_save_path = os.path.join('./models', "model_jit.pt")
    torch.save(model.state_dict(), model_save_path)
    script_cell = torch.jit.script(model)
    torch.jit.save(script_cell, jit_model_save_path)

if __name__ == "__main__":
    args = docopt(__doc__)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_depth_input = False
    use_other_inputs = False
    if use_depth_input:
        in_channels = 4
    else:
        in_channels = 3
    random_split_seed = 22
    test_data_percentage = 20
    learning_rate = 0.0001
    batch_size = 256
    num_epochs = 10

    model = Linear(in_channels=in_channels).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.MSELoss()

    dataset = Load_Data(args["<data_dir>"], use_depth_input=use_depth_input, use_other_inputs=use_other_inputs)
    test_len = math.floor(len(dataset) * test_data_percentage / 100)
    train_set, test_set = torch.utils.data.random_split(dataset, [len(dataset)-test_len, test_len], generator=torch.Generator().manual_seed(random_split_seed))
    train_set_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
    test_set_loader = DataLoader(dataset=test_set, batch_size=batch_size, shuffle=True)

    train(device, model, criterion, optimizer, train_set_loader, test_set_loader, use_other_inputs=use_other_inputs)

    # Saving the model
    save_model()