"""
Usage:
    train.py  <data_dirs>... [--model=None] [--name=None]

Options:
  -h --help     Show this screen.
"""

from networks import Linear
from networks import Linear_With_Others
from data_loader import Load_Data

from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader
from prettytable import PrettyTable
from docopt import docopt
from tqdm import tqdm
import torchvision
import logging
import torch
import math
import sys
import os

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("train")


def main():
    # Hyperparameters
    # If reduce_resolution == None zed's resolution will be used
    # None or {"height": x, "width": y}
    reduce_resolution = {"height": 120, "width": 160}
    # If set to value like 30 it will make training data ~30fps 
    # It wont work great if datasets fps is close to reduce_fps
    reduce_fps = False
    use_depth = False
    # False or list like ["IMU_Accel_X", "IMU_Accel_Y", "IMU_Accel_Z", "IMU_Gyro_X", "IMU_Gyro_Y", "IMU_Gyro_Z", "Speed"]
    other_inputs = False
    # 2e-3 for startup then reduce to 1e-3
    learning_rate = 2e-3
    batch_size = 1024
    num_epochs = 250
    test_data_percentage = 20
    # Saves image grid for first trrain and test set
    detailed_tensorboard = False

    args = docopt(__doc__)
    data_dirs = args["<data_dirs>"]
    model_path = args["--model"]
    model_save_name = args["--name"]
    if not model_save_name:
        model_save_name = "model"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(22)

    if use_depth:
        in_channels = 4
    else:
        in_channels = 3

    # Our input size is not changing so we can use cudnn's optimization
    torch.backends.cudnn.benchmark = True

    model = Linear(in_channels=in_channels).to(device)
    if model_path:
        model.load_state_dict(torch.load(model_path))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.MSELoss()

    writer = SummaryWriter(f"tb_logs/{model_save_name}")
    example_input = torch.ones((1, in_channels, reduce_resolution["height"], reduce_resolution["width"]), device=device)
    if other_inputs:
        example_input = (example_input, torch.ones(1, (len(other_inputs)), device=device))
    writer.add_graph(model, input_to_model=example_input, verbose=False, use_strict_trace=True)

    dataset = Load_Data(data_dirs, reduce_resolution=reduce_resolution, reduce_fps=reduce_fps, use_depth=use_depth, other_inputs=other_inputs)
    test_len = math.floor(len(dataset) * test_data_percentage / 100)
    train_set, test_set = torch.utils.data.random_split(dataset, [len(dataset)-test_len, test_len])
    # train_set = torch.utils.data.Subset(train_set, range(int(len(train_set)/2)))
    # test_set = torch.utils.data.Subset(dataset, range(len(dataset)-test_len, len(dataset)))
    # We using torch.backends.cudnn.benchmark 
    # it will be slow if input size change (batch size is changing on last layer if data_set_len%batch_size!=0) so we set drop_last = True
    train_set_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True, drop_last=True)
    test_set_loader = DataLoader(dataset=test_set, batch_size=batch_size, num_workers=4, pin_memory=True)

    if detailed_tensorboard:
        # Adding train and test images from first batch to tensorboard
        data = next(iter(train_set_loader))
        # We using BGR image format but tensorboard expects rgb so we converting it to RGB with flip on channel dimension
        images = torch.flip(data[0], [1])
        grid = torchvision.utils.make_grid(images)
        writer.add_image(f"Train Set First Batch", grid, 0)
        if test_data_percentage:
            data = next(iter(test_set_loader))
            images = torch.flip(data[0], [1])
            grid = torchvision.utils.make_grid(images)
            writer.add_image(f"Test Set First Batch", grid, 0)

    trainer = Trainer(model, criterion, optimizer, device, num_epochs, train_set_loader, writer=writer, test_set_loader=test_set_loader, model_name=model_save_name, other_inputs=other_inputs, patience=5, delta=0.00005)
    trainer.fit()
    writer.close()


class Trainer:
    def __init__(self, model, criterion, optimizer, device, num_epochs, train_set_loader, writer=None, test_set_loader=None, model_name="model", other_inputs=False, patience=5, delta=0.00005):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.train_set_loader = train_set_loader
        self.writer = writer
        self.test_set_loader = test_set_loader
        self.model_name = model_name
        self.other_inputs = other_inputs
        self.num_epochs = num_epochs
        # Delta: Minimum change to qualify as an improvement.
        # Patience:  How many times we wait for change < delta before stop training.
        self.patience = patience
        self.delta = delta

        self.loss_table = PrettyTable()
        self.loss_table.field_names = ["", "Total", "Steering", "Throttle"]
        # If we don't know the inverse of self.criterion it will return None
        self.convert_loss_to_pwm = self.inverse_loss(0) != None
        self.nu_of_train_batches = len(self.train_set_loader)
        if self.test_set_loader:
            self.nu_of_test_batches = len(self.test_set_loader)
        self.train_not_improved_count = 0
        self.test_not_improved_count = 0
        self.train_set_min_loss = float('inf')
        self.test_set_min_loss = float('inf')
        self.steering_weight = 0.9
        self.throttle_weight = 0.1

    def fit(self):
        # torch.autograd.set_detect_anomaly(True)
        # logger.info(self.model)
        logger.info(f"Trainig on {self.device}...")
        epoch_losses = dict(steering=[], throttle=[], loss=[])
        for epoch in range(1, self.num_epochs+1):
            self.model.train()
            pbar = tqdm(self.train_set_loader, desc=f"Epoch: {epoch} ", file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}')
            batch_losses = dict(steering=[], throttle=[], loss=[])
            for batch_no, data in enumerate(pbar, 1):
                for param in self.model.parameters():
                    param.grad = None
                if self.other_inputs:
                    images, other_inputs, steering_labels, throttle_labels = data
                    other_inputs = other_inputs.to(self.device)
                else:
                    images, steering_labels, throttle_labels = data
                # Normalizing the image
                images = images.to(self.device, non_blocking=True) / 255.0
                steering_labels = steering_labels.to(self.device)
                throttle_labels = throttle_labels.to(self.device)
                if self.other_inputs:
                    steering_prediction, throttle_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, throttle_prediction = self.model(images)
                batch_steering_loss = self.criterion(steering_prediction, steering_labels)
                batch_throttle_loss = self.criterion(throttle_prediction, throttle_labels)
                batch_loss = self.steering_weight * batch_steering_loss + self.throttle_weight * batch_throttle_loss
                batch_losses["steering"].append(batch_steering_loss.item())
                batch_losses["throttle"].append(batch_throttle_loss.item())
                batch_losses["loss"].append(batch_loss.item())
                logger.info(f"\nBatch[{batch_no}/{self.nu_of_train_batches}] Loss: {batch_loss:.4f}, Steering Loss: {batch_steering_loss:.4f}, Throttle Loss: {batch_throttle_loss:.4f}")
                batch_loss.backward()
                # Gradient clipping
                # torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5)
                self.optimizer.step()
            # After finishing epoch we evaluating the model
            epoch_steering_loss = sum(batch_losses["steering"]) / batch_no
            epoch_throttle_loss = sum(batch_losses["throttle"]) / batch_no
            epoch_loss = sum(batch_losses["loss"]) / batch_no
            epoch_losses["steering"].append(epoch_steering_loss)
            epoch_losses["throttle"].append(epoch_throttle_loss)
            epoch_losses["loss"].append(epoch_loss)
            self.loss_table.add_row(["Train", f"{epoch_loss:.4f}", f"{epoch_steering_loss:.4f}", f"{epoch_throttle_loss:.4f}"])
            if self.convert_loss_to_pwm:
                self.loss_table.add_row(["PWM", f"{self.inverse_loss(epoch_loss):.4f}", f"{self.inverse_loss(epoch_steering_loss):.4f}", f"{self.inverse_loss(epoch_throttle_loss):.4f}"])
            if self.test_set_loader:
                logger.info("\nEvaluating on test set ...")
                eval_loss, eval_steering_loss, eval_throttle_loss = self.evaluate()
                self.loss_table.add_row(["Val", f"{eval_loss:.4f}", f"{eval_steering_loss:.4f}", f"{eval_throttle_loss:.4f}"])
                if self.convert_loss_to_pwm:
                    self.loss_table.add_row(["Val PWM", f"{self.inverse_loss(eval_loss):.4f}", f"{self.inverse_loss(eval_steering_loss):.4f}", f"{self.inverse_loss(eval_throttle_loss):.4f}"])
            self.loss_table.sortby = 'Total'
            logger.info(f"\n{self.loss_table}\n")
            self.loss_table.clear_rows()

            if self.writer:
                self.writer.add_scalar('Train/Loss', epoch_loss, epoch)
                self.writer.add_scalar('Train/Steering_Loss', epoch_steering_loss, epoch)
                self.writer.add_scalar('Train/Throttle_Loss', epoch_throttle_loss, epoch)
                if self.test_set_loader:
                    self.writer.add_scalar('Test/Loss', eval_loss, global_step=epoch)
                    self.writer.add_scalar('Test/Steering_Loss', eval_steering_loss, global_step=epoch)
                    self.writer.add_scalar('Test/Throttle_Loss', eval_throttle_loss, global_step=epoch)
                self.writer.flush()

            # Checking if there is an improvement
            # We counting as improvement if delta_loss > self.delta
            delta_train_set_loss =  self.train_set_min_loss - epoch_loss
            if delta_train_set_loss > 0:
                self.train_set_min_loss = epoch_loss
                if delta_train_set_loss >= self.delta:
                    self.train_not_improved_count = 0
                else:
                    self.train_not_improved_count += 1
            if self.test_set_loader:
                delta_test_set_loss =  self.test_set_min_loss - eval_loss
                if delta_test_set_loss > 0:
                    self.test_set_min_loss = eval_loss
                    if delta_test_set_loss >= self.delta:
                        self.test_not_improved_count = 0
                    else:
                        self.test_not_improved_count += 1

            # If this model is better than previous model we saving it
            if delta_test_set_loss > 0:
                self.save_model()
            # Early stopping
            # If loss improve smaller than delta for patience times stops training 
            if (self.train_not_improved_count >= self.patience):
                logger.info(f"Stopped Training: Delta Loss Is Smaller Than {self.delta} For {self.patience} Times")
                break

    def inverse_loss(self, loss):
        # If you want to convert loss to pwm differance you must add the loss functions inverse here
        # If loss functions inverse isn't written this functionality won't be used
        if str(self.criterion) == "MSELoss()":
            # Inverse of MSELoss
            return math.sqrt(loss) * 500
        else:
            return None

    def evaluate(self):
        self.model.eval()
        losses = dict(steering=[], throttle=[], loss=[])
        with torch.no_grad():
            for batch_no, data in enumerate(tqdm(self.test_set_loader, file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}'), 1):
                if self.other_inputs:
                    images, other_inputs, steering_labels, throttle_labels = data
                    other_inputs = other_inputs.to(self.device)
                else:
                    images, steering_labels, throttle_labels = data
                images = images.to(self.device, non_blocking=True) / 255.0
                steering_labels = steering_labels.to(self.device)
                throttle_labels = throttle_labels.to(self.device)
                if self.other_inputs:  
                    steering_prediction, throttle_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, throttle_prediction = self.model(images)
                steering_loss = self.criterion(steering_prediction, steering_labels)
                throttle_loss = self.criterion(throttle_prediction, throttle_labels)
                loss = self.steering_weight * steering_loss + self.throttle_weight * throttle_loss
                losses["steering"].append(steering_loss)
                losses["throttle"].append(throttle_loss)
                losses["loss"].append(loss)
        eval_steering_loss = sum(losses["steering"]) / batch_no
        eval_throttle_loss = sum(losses["throttle"]) / batch_no
        eval_loss = sum(losses["loss"]) / batch_no
        return eval_loss, eval_steering_loss, eval_throttle_loss

    def save_model(self):
        model_save_path = os.path.join(os.path.expanduser('~'), "e2e-driver", "models")
        torch.save(self.model.state_dict(), os.path.join(model_save_path, self.model_name + ".pt"))
        script_cell = torch.jit.script(self.model)
        torch.jit.save(script_cell, os.path.join(model_save_path, self.model_name + ".jit"))
        logger.info(f"Saved the model to {os.path.join(model_save_path, self.model_name)}\n")


if __name__ == "__main__":
    main()