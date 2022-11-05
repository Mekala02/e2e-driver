"""
Usage:
    train.py  <data_dirs>... [--model=None]

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
    torch.manual_seed(22)
    use_depth_input = False
    use_other_inputs = False
    if use_depth_input:
        in_channels = 4
    else:
        in_channels = 3
    test_data_percentage = 10
    #2e-3 for startup then reduce to 1e-3
    learning_rate = 2e-3
    batch_size = 1024
    num_epochs = 100

    # Our input size is not changing so we can use cudnn's optimization
    torch.backends.cudnn.benchmark = True

    model_path = args["--model"]
    model = Linear(in_channels=in_channels).to(device)
    if model_path:
        model.load_state_dict(torch.load(model_path))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.MSELoss()

    dataset = Load_Data(args["<data_dirs>"], use_depth_input=use_depth_input, use_other_inputs=use_other_inputs)
    test_len = math.floor(len(dataset) * test_data_percentage / 100)
    train_set, test_set = torch.utils.data.random_split(dataset, [len(dataset)-test_len, test_len])
    # We using torch.backends.cudnn.benchmark 
    # it will be slow if input size change (batch size is changing on last layer if data_set_len%batch_size!=0) so we set drop_last = True
    train_set_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True, drop_last=True)
    test_set_loader = DataLoader(dataset=test_set, batch_size=batch_size, num_workers=4, pin_memory=True)
    trainer = Trainer(model, criterion, optimizer, device, num_epochs, train_set_loader, test_set_loader=test_set_loader, use_other_inputs=False, patience=5, delta=0.00005)
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
        self.not_improved_count = 0
        self.train_set_min_loss = float('inf')
        self.test_set_min_loss = float('inf')
        self.steering_weight = 0.9
        self.throttle_weight = 0.1

    def fit(self):
        # torch.autograd.set_detect_anomaly(True)
        # logger.info(self.model)
        logger.info(f"Trainig on {self.device}...")
        for epoch in range(1, self.num_epochs+1):
            epoch_steering_losses = []
            epoch_throttle_losses = []
            epoch_losses = []
            self.model.train()
            pbar = tqdm(self.train_set_loader, desc=f"Epoch: {epoch} ", file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}')
            for batch_no, data in enumerate(pbar, 1):
                batch_steering_losses = []
                batch_throttle_losses = []
                batch_losses = []
                for param in self.model.parameters():
                    param.grad = None
                if self.use_other_inputs:
                    images, other_inputs, steering_labels, throttle_labels = data
                    other_inputs = other_inputs.to(self.device)
                else:
                    images, steering_labels, throttle_labels = data
                images = images.to(self.device, non_blocking=True) / 255.0
                steering_labels = steering_labels.to(self.device)
                throttle_labels = throttle_labels.to(self.device)
                if self.use_other_inputs:
                    steering_prediction, throttle_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, throttle_prediction = self.model(images)
                batch_steering_loss = self.criterion(steering_prediction, steering_labels)
                batch_throttle_loss = self.criterion(throttle_prediction, throttle_labels)
                batch_loss = self.steering_weight * batch_steering_loss + self.throttle_weight * batch_throttle_loss
                batch_steering_losses.append(batch_steering_loss.item())
                batch_throttle_losses.append(batch_throttle_loss.item())
                batch_losses.append(batch_loss.item())
                logger.info(f"\nBatch[{batch_no}/{self.nu_of_train_batches}] Loss: {batch_loss:.2e}, Steering Loss: {batch_steering_loss:.2e}, Throttle Loss: {batch_throttle_loss:.2e}")
                batch_loss.backward()
                # Gradient clipping
                # torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5)
                self.optimizer.step()
            
            # After finishing epoch we evaluating the model
            epoch_steering_loss = sum(batch_steering_losses) / len(batch_steering_losses)
            epoch_throttle_loss = sum(batch_throttle_losses) / len(batch_throttle_losses)
            epoch_loss = sum(batch_losses) / len(batch_losses)
            epoch_steering_losses.append(epoch_steering_loss)
            epoch_throttle_losses.append(epoch_throttle_loss)
            epoch_losses.append(epoch_loss)
            loss_string = f"For Epoch {epoch} --> Loss: {epoch_loss:.2e}, Steering Loss: {epoch_steering_loss:.2e}, Throttle Loss: {epoch_throttle_loss:.2e}"
            if self.test_set_loader:
                logger.info("\nEvaluating on test set ...")
                eval_loss, eval_steering_loss, eval_throttle_loss = self.evaluate()
                val_loss_string = f"Val Loss: {eval_loss:.2e} Steering Val Loss: {eval_steering_loss:.2e}, Throttle Val Loss: {eval_throttle_loss:.2e}"
                logger.info(val_loss_string + " - " + loss_string + '\n')
            else:
                logger.info(loss_string + '\n')
            # If this model is better than previous model we saving it
            # If we have test set we desiding improvement based on that
            self.not_improved_count += 1
            delta_train_set_loss =  self.train_set_min_loss - epoch_loss
            if delta_train_set_loss > 0:
                self.train_set_min_loss = epoch_loss
                # We counting as improvement if delta_loss > self.delta
                if delta_train_set_loss >= self.delta and not self.test_set_loader:
                    self.not_improved_count = 0
            if self.test_set_loader:
                delta_test_set_loss =  self.test_set_min_loss - eval_loss
                if delta_test_set_loss > 0:
                    self.test_set_min_loss = eval_loss
                    if delta_test_set_loss >= self.delta:
                        self.not_improved_count = 0
            # saving the model if improved
            if self.not_improved_count == 0:
                self.save_model()
            # Early stopping
            # If loss improve smaller than delta for patience times stops training 
            if (self.not_improved_count >= self.patience):
                logger.info(f"Stopped Training: Delta Loss Is Smaller Than {self.delta} For {self.patience} Times")
                break

    def evaluate(self):
        self.model.eval()
        steering_losses = []
        throttle_losses = []
        losses = []
        with torch.no_grad():
            for batch_no, data in enumerate(tqdm(self.test_set_loader, file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}'), 1):
                if self.use_other_inputs:
                    images, other_inputs, steering_labels, throttle_labels = data
                    other_inputs = other_inputs.to(self.device)
                else:
                    images, steering_labels, throttle_labels = data
                images = images.to(self.device, non_blocking=True) / 255.0
                steering_labels = steering_labels.to(self.device)
                throttle_labels = throttle_labels.to(self.device)
                if self.use_other_inputs:  
                    steering_prediction, throttle_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, throttle_prediction = self.model(images)
                steering_loss, throttle_loss = self.criterion(steering_prediction, steering_labels), self.criterion(throttle_prediction, throttle_labels)
                loss = self.steering_weight * steering_loss + self.throttle_weight * throttle_loss
                steering_losses.append(steering_loss)
                throttle_losses.append(throttle_loss)
                losses.append(loss)
                # logger.info(f"\nTest Set--> Batch[{batch_no}/{self.nu_of_test_batches}] Loss: {loss:.2e}, Steering Loss: {steering_loss:.2e}, Throttle Loss: {throttle_loss:.2e}")
        eval_steering_loss = sum(steering_losses) / len(steering_losses)
        eval_throttle_loss = sum(throttle_losses) / len(throttle_losses)
        eval_loss = sum(losses) / len(losses)
        return eval_loss, eval_steering_loss, eval_throttle_loss

    def save_model(self):
        model_save_path = os.path.join('~/e2e-driver/models', "model.pt")
        jit_model_save_path = os.path.join('~/e2e-driver/models', "model_jit.pt")
        torch.save(self.model.state_dict(), model_save_path)
        script_cell = torch.jit.script(self.model)
        torch.jit.save(script_cell, jit_model_save_path)
        logger.info(f"Saved the model to {model_save_path}\n")


if __name__ == "__main__":
    main()