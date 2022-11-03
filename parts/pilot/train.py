"""
Usage:
    train.py  <data_dir> [<model>]

Options:
  -h --help     Show this screen.
"""

from networks import Linear
from data_loader import Load_Data

from torch.utils.data import DataLoader
from docopt import docopt
from tqdm import tqdm
import logging
import sys
import torch
import math
import os

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("train")


def main():
    args = docopt(__doc__)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_depth_input = False
    use_other_inputs = False
    if use_depth_input:
        in_channels = 4
    else:
        in_channels = 3
    random_split_seed = 22
    test_data_percentage = 10
    learning_rate = 0.0001
    batch_size = 256
    num_epochs = 10

    model_path = args["<model>"]
    model = Linear(in_channels=in_channels).to(device)
    if model_path:
        model.load_state_dict(torch.load(model_path))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.MSELoss()

    dataset = Load_Data(args["<data_dir>"], device, use_depth_input=use_depth_input, use_other_inputs=use_other_inputs)
    test_len = math.floor(len(dataset) * test_data_percentage / 100)
    train_set, test_set = torch.utils.data.random_split(dataset, [len(dataset)-test_len, test_len], generator=torch.Generator().manual_seed(random_split_seed))
    train_set_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
    test_set_loader = DataLoader(dataset=test_set, batch_size=batch_size, shuffle=True)

    trainer = Trainer(model, criterion, optimizer, device, num_epochs, train_set_loader, test_set_loader=test_set_loader, use_other_inputs=False, patience=3, delta=0.0005)
    trainer.fit()
    # Saving the model
    # trainer.save_model()


class Trainer:
    def __init__(self, model, criterion, optimizer, device, num_epochs, train_set_loader, test_set_loader=None, use_other_inputs=False, patience=3, delta=0.0005):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.train_set_loader = train_set_loader
        self.test_set_loader = test_set_loader
        self.use_other_inputs = use_other_inputs
        self.num_epochs = num_epochs
        # Delta: Minimum change to qualify as an improvement.
        # Patience:  How many times we wait for change < delta before stop training.
        self.patience = patience
        self.delta = delta

        self.nu_of_train_batches = len(self.train_set_loader)
        if self.test_set_loader:
            self.nu_of_test_batches = len(self.test_set_loader)
        self.train_set_min_loss = float('inf')
        self.test_set_min_loss = float('inf')

    def fit(self):
        # torch.autograd.set_detect_anomaly(True)
        # logger.info(self.model)
        logger.info(f"Trainig on {self.device}...")
        epoch_steering_losses = []
        epoch_throttle_losses = []
        for epoch in range(1, self.num_epochs+1):
            self.model.train()
            batch_steering_losses = []
            batch_throttle_losses = []
            pbar = tqdm(self.train_set_loader, desc=f"Epoch: {epoch}", file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}')
            for batch_no, data in enumerate(pbar, 1):
                self.optimizer.zero_grad()
                if self.use_other_inputs:
                    images, other_inputs, steering_labels, throttle_labels = data
                else:
                    images, steering_labels, throttle_labels = data
                # Forward
                if self.use_other_inputs:
                    steering_prediction, throttle_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, throttle_prediction = self.model(images)
                batch_steering_loss = self.criterion(steering_prediction, steering_labels)
                batch_throttle_loss = self.criterion(throttle_prediction, throttle_labels)
                total_loss = batch_steering_loss + batch_throttle_loss
                batch_steering_losses.append(batch_steering_loss.item())
                batch_throttle_losses.append(batch_throttle_loss.item())
                logger.info(f"\nBatch[{batch_no}/{self.nu_of_train_batches}] Total Loss: {total_loss:.2e}, Steering Loss: {batch_steering_loss:.2e}, Throttle Loss: {batch_throttle_loss:.2e}")
                # Backward
                total_loss.backward()
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5)
                # Gradient Descent Step
                self.optimizer.step()
            # After finishing epoch we evaluating the model
            epoch_steering_loss = sum(batch_steering_losses) / len(batch_steering_losses)
            epoch_throttle_loss = sum(batch_throttle_losses) / len(batch_throttle_losses)
            epoch_total_loss = epoch_steering_loss + epoch_throttle_loss
            epoch_steering_losses.append(epoch_steering_loss)
            epoch_throttle_losses.append(epoch_throttle_loss)
            loss_string = f"For Epoch {epoch} --> Total Loss: {epoch_steering_loss:.2e}, Steering Loss: {epoch_throttle_loss:.2e}, Throttle Loss: {epoch_total_loss:.2e}"
            if self.test_set_loader:
                logger.info("Evaluating on test set ...")
                eval_total_loss, eval_steering_loss, eval_throttle_loss = self.evaluate()
                val_loss_string = f"Total Val Loss: {eval_total_loss:.2e} Steering Val Loss: {eval_steering_loss:.2e}, Throttle Val Loss: {eval_throttle_loss:.2e}"
                logger.info(loss_string + " - " + val_loss_string)
            else:
                logger.info(loss_string)
            # If this model is better than previous model we saving it
            # If we evaluate on test set we saving according to that
            if epoch_total_loss < self.train_set_min_loss:
                self.train_set_min_loss = epoch_total_loss
                if not self.test_set_loader:
                    self.save_model()
            if self.test_set_loader:
                if eval_total_loss < self.test_set_min_loss:
                    self.test_set_min_loss = eval_total_loss
                    self.save_model()

            # Early stopping
            if batch_no >= self.patience:
                last_index = batch_no-1
                epochs_total_losses = sum(epoch_steering_losses) + sum(epoch_throttle_losses)
                # If loss improve smaller than delta for patience times stops training 
                if (epochs_total_losses[last_index] - epochs_total_losses[last_index-1] < self.delta) and (epochs_total_losses[last_index-1] - epochs_total_losses[last_index-2] < self.delta):
                    logger.info(f"Stopped Training: Delta Loss Is Smaller Than {self.delta} For {self.patience} Times")
                    break

    def evaluate(self):
        logger.info("Evaluation Mode")
        self.model.eval()
        steering_losses = []
        throttle_losses = []
        with torch.no_grad():
            for batch_no, data in enumerate(tqdm(self.test_set_loader, file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}'), 1):
                if self.use_other_inputs:
                    images, other_inputs, steering_labels, throttle_labels = data
                else:
                    images, steering_labels, throttle_labels = data
                if self.use_other_inputs:  
                    steering_prediction, throttle_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, throttle_prediction = self.model(images)
                steering_loss, throttle_loss = self.criterion(steering_prediction, steering_labels), self.criterion(throttle_prediction, throttle_labels)
                total_loss = steering_loss + throttle_loss
                steering_losses.append(steering_loss)
                throttle_losses.append(throttle_loss)
                logger.info(f"\nTest Set--> Batch[{batch_no}/{self.nu_of_test_batches}] Total Loss: {total_loss:.2e}, Steering Loss: {steering_loss:.2e}, Throttle Loss: {throttle_loss:.2e}")
        eval_steering_loss = sum(steering_losses) / len(steering_losses)
        eval_throttle_loss = sum(throttle_losses) / len(throttle_losses)
        eval_total_loss = eval_steering_loss + eval_throttle_loss
        return eval_total_loss, eval_steering_loss, eval_throttle_loss

    def save_model(self):
        model_save_path = os.path.join('./models', "model.pt")
        jit_model_save_path = os.path.join('./models', "model_jit.pt")
        torch.save(self.model.state_dict(), model_save_path)
        script_cell = torch.jit.script(self.model)
        torch.jit.save(script_cell, jit_model_save_path)
        logger.info(f"Saved the model to {model_save_path}")


if __name__ == "__main__":
    main()