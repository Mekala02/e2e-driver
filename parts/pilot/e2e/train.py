"""
Usage:
    train.py  <data_dirs>... [--test_dirs=<test_dirs>]... [--model=<pretrained_model>] [--name=<models_name>]
    
Options:
  -h --help                     Show this screen.
  --test_dirs=<test_dirs>       Specify seperate test set
  --model=<pretrained_model>    Pretrained model
  --name=<models_name>          Model's name
"""
from data_loader import Load_Data
from train_config import Train_Config as t_cfg
from train_config import TRANSFORMS, TRAIN_TRANSFORMS

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
    in_channels = 4 if t_cfg["USE_DEPTH"] else 3
    model = t_cfg["MODEL"](in_channels=in_channels).to(device)
    criterion = t_cfg["CRITERION"]()
    optimizer = t_cfg["OPTIMIZER"](model.parameters(), lr=t_cfg["LEARNING_RATE"])

    torch.manual_seed(22)
    if t_cfg["USE_CUDNN_BENCHMARK"]:
        torch.backends.cudnn.benchmark = True

    if model_path:
        model.load_state_dict(torch.load(model_path))

    train_set = Load_Data(data_dirs, act_value_type=t_cfg["ACT_VALUE_TYPE"], transform=TRAIN_TRANSFORMS, reduce_fps=t_cfg["REDUCE_FPS"], use_depth=t_cfg["USE_DEPTH"], other_inputs=t_cfg["OTHER_INPUTS"])

    test_sets = []
    if t_cfg["VALIDATION_SPLIT"]:
        test_set = Load_Data(data_dirs, act_value_type=t_cfg["ACT_VALUE_TYPE"], transform=TRANSFORMS, reduce_fps=t_cfg["REDUCE_FPS"], use_depth=t_cfg["USE_DEPTH"], other_inputs=t_cfg["OTHER_INPUTS"])
        assert len(train_set) == len(test_set)
        len_dataset = len(train_set)
        test_len = math.floor(len_dataset * t_cfg["VALIDATION_SPLIT"])
        train_set = torch.utils.data.random_split(train_set, [len_dataset-test_len, test_len])[0]
        test_sets.append(torch.utils.data.random_split(test_set, [len_dataset-test_len, test_len])[1])
    if test_dirs:
        test_sets.append(Load_Data(test_dirs, act_value_type=t_cfg["ACT_VALUE_TYPE"], transform=TRANSFORMS, reduce_fps=t_cfg["REDUCE_FPS"], use_depth=t_cfg["USE_DEPTH"], other_inputs=t_cfg["OTHER_INPUTS"]))

    trainloader = DataLoader(dataset=train_set, batch_size=t_cfg["BATCH_SIZE"], shuffle=t_cfg["SHUFFLE_TRAINSET"], num_workers=4, pin_memory=True, drop_last=t_cfg["DROP_LAST"])
    if test_sets:
        testlaoder = DataLoader(dataset=torch.utils.data.ConcatDataset(test_sets), batch_size=t_cfg["BATCH_SIZE"], num_workers=4, pin_memory=True)
    else:
        testlaoder = None

    if t_cfg["USE_TB"]:
        writer = SummaryWriter(f"tb_logs/{model_save_name}")
        if t_cfg["TB_ADD_GRAPH"]:
            example_input = torch.ones((1, in_channels, t_cfg["IMAGE_RESOLUTION"]["height"], t_cfg["IMAGE_RESOLUTION"]["width"]), device=device)
            if t_cfg["OTHER_INPUTS"]:
                example_input = (example_input, torch.ones(1, (len(t_cfg["OTHER_INPUTS"])), device=device))
            writer.add_graph(model, input_to_model=example_input, verbose=False, use_strict_trace=True)
        if t_cfg["DETAILED_TB"]:
            # Adding train and test images from first batch to tensorboard
            data = next(iter(trainloader))
            # We using BGR image format but tensorboard expects rgb so we converting it to RGB with flip on channel dimension
            images = torch.flip(data[0], [1])
            grid = torchvision.utils.make_grid(images)
            writer.add_image(f"Train Set First Batch", grid, 0)
            if testlaoder:
                data = next(iter(testlaoder))
                images = torch.flip(data[0], [1])
                grid = torchvision.utils.make_grid(images)
                writer.add_image(f"Test Set First Batch", grid, 0)
    else: writer=None

    trainer = Trainer(model, criterion, optimizer, device, t_cfg["NUM_EPOCHS"], trainloader, t_cfg["ACT_VALUE_TYPE"], writer=writer, testlaoder=testlaoder,
                    model_name=model_save_name, other_inputs=t_cfg["OTHER_INPUTS"], patience=t_cfg["PATIENCE"], delta=t_cfg["DELTA"])
    trainer.fit()
    if t_cfg["USE_TB"]:
        writer.close()

class Trainer:
    def __init__(self, model, criterion, optimizer, device, num_epochs, trainloader, act_value_type, writer=None, testlaoder=None, model_name="model", other_inputs=False, patience=5, delta=0.00005):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.trainloader = trainloader
        self.act_value_type = act_value_type
        self.writer = writer
        self.testlaoder = testlaoder
        self.model_name = model_name
        self.other_inputs = other_inputs
        self.num_epochs = num_epochs
        self.patience = patience
        self.delta = delta

        self.loss_table = PrettyTable()
        self.loss_table.field_names = ["", "Total", "Steering", self.act_value_type]
        # If we don't know the inverse of self.criterion it will return None
        self.convert_loss_to_pwm = self.inverse_loss(0) != None
        self.nu_of_train_batches = len(self.trainloader)
        if self.testlaoder:
            self.nu_of_test_batches = len(self.testlaoder)
        self.train_not_improved_count = 0
        self.test_not_improved_count = 0
        self.train_set_min_loss = float('inf')
        self.test_set_min_loss = float('inf')
        self.steering_weight = 0.9
        self.act_value_weight = 0.1

    def fit(self):
        # torch.autograd.set_detect_anomaly(True)
        # logger.info(self.model)
        logger.info(f"Trainig on {self.device}...")
        epoch_losses = dict(steering=[], act_value=[], loss=[])
        for epoch in range(1, self.num_epochs+1):
            self.model.train()
            pbar = tqdm(self.trainloader, desc=f"Epoch: {epoch} ", file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}')
            batch_losses = dict(steering=[], act_value=[], loss=[])
            for batch_no, data in enumerate(pbar, 1):
                for param in self.model.parameters():
                    param.grad = None
                if self.other_inputs:
                    images, other_inputs, steering_labels, act_value_labels = data
                    other_inputs = other_inputs.to(self.device)
                else:
                    images, steering_labels, act_value_labels = data
                # Normalizing the inputs
                images = self.normalize_image(images.to(self.device, non_blocking=True))
                steering_labels = steering_labels.to(self.device, non_blocking=True)
                act_value_labels = act_value_labels.to(self.device, non_blocking=True)
                if self.other_inputs:
                    steering_prediction, act_value_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, act_value_prediction = self.model(images)
                batch_steering_loss = self.criterion(steering_prediction, steering_labels)
                batch_act_value_loss = self.criterion(act_value_prediction, act_value_labels)
                batch_loss = self.steering_weight * batch_steering_loss + self.act_value_weight * batch_act_value_loss
                batch_losses["steering"].append(batch_steering_loss.item())
                batch_losses["act_value"].append(batch_act_value_loss.item())
                batch_losses["loss"].append(batch_loss.item())
                logger.info(f"\nBatch[{batch_no}/{self.nu_of_train_batches}] Loss: {batch_loss:.4f}, Steering Loss: {batch_steering_loss:.4f}, {self.act_value_type} Loss: {batch_act_value_loss:.4f}")
                batch_loss.backward()
                # Gradient clipping
                # torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5)
                self.optimizer.step()
            # After finishing epoch we evaluating the model
            epoch_steering_loss = sum(batch_losses["steering"]) / batch_no
            epoch_act_value_loss = sum(batch_losses["act_value"]) / batch_no
            epoch_loss = sum(batch_losses["loss"]) / batch_no
            epoch_losses["steering"].append(epoch_steering_loss)
            epoch_losses["act_value"].append(epoch_act_value_loss)
            epoch_losses["loss"].append(epoch_loss)
            self.loss_table.add_row(["Train", f"{epoch_loss:.4f}", f"{epoch_steering_loss:.4f}", f"{epoch_act_value_loss:.4f}"])
            if self.convert_loss_to_pwm:
                self.loss_table.add_row(["I Train", f"{self.inverse_loss(epoch_loss):.4f}", f"{self.inverse_loss(epoch_steering_loss):.4f}", f"{self.inverse_loss(epoch_act_value_loss):.4f}"])
            if self.testlaoder:
                logger.info("\nEvaluating on test set ...")
                eval_loss, eval_steering_loss, eval_act_value_loss = self.evaluate()
                self.loss_table.add_row(["Val", f"{eval_loss:.4f}", f"{eval_steering_loss:.4f}", f"{eval_act_value_loss:.4f}"])
                if self.convert_loss_to_pwm:
                    self.loss_table.add_row(["I Val", f"{self.inverse_loss(eval_loss):.4f}", f"{self.inverse_loss(eval_steering_loss):.4f}", f"{self.inverse_loss(eval_act_value_loss):.4f}"])
            self.loss_table.sortby = 'Total'
            logger.info(f"\n{self.loss_table}\n")
            self.loss_table.clear_rows()

            if self.writer:
                self.writer.add_scalar("Train/Loss", epoch_loss, epoch)
                self.writer.add_scalar("Train/Steering_Loss", epoch_steering_loss, epoch)
                self.writer.add_scalar(f"Train/{self.act_value_type}_Loss", epoch_act_value_loss, epoch)
                if self.testlaoder:
                    self.writer.add_scalar("Test/Loss", eval_loss, global_step=epoch)
                    self.writer.add_scalar("Test/Steering_Loss", eval_steering_loss, global_step=epoch)
                    self.writer.add_scalar(f"Test/{self.act_value_type}_Loss", eval_act_value_loss, global_step=epoch)
                self.writer.flush()

            # If this model is better than previous model we saving it
            if self.testlaoder:
                if eval_loss < self.test_set_min_loss:
                    self.save_model()
            else:
                if epoch_loss < self.train_set_min_loss:
                    self.save_model()

            # Checking if there is an improvement
            # We counting as improvement if delta_loss > self.delta
            if epoch_loss + self.delta < self.train_set_min_loss:
                    self.train_not_improved_count = 0
            else:
                self.train_not_improved_count += 1
            self.train_set_min_loss = min(self.train_set_min_loss, epoch_loss)

            if self.testlaoder:
                if eval_loss + self.delta < self.test_set_min_loss:
                    self.test_not_improved_count = 0
                else:
                    self.test_not_improved_count += 1
                self.test_set_min_loss = min(self.test_set_min_loss, eval_loss)

            # Early stopping
            # If loss improve smaller than delta for patience times stops training 
            if (self.train_not_improved_count >= self.patience):
                logger.info(f"Stopped Training: Delta Loss Is Smaller Than {self.delta} For {self.patience} Times")
                break


    def inverse_loss(self, loss):
        # If you want to convert loss to pwm differance you must add the loss functions inverse here
        # If loss functions inverse isn't written, this functionality won't be used
        if str(self.criterion) == "MSELoss()":
            # Inverse of MSELoss
            return math.sqrt(loss)
        return None

    def evaluate(self):
        self.model.eval()
        losses = dict(steering=[], act_value=[], loss=[])
        with torch.no_grad():
            for batch_no, data in enumerate(tqdm(self.testlaoder, file=sys.stdout, bar_format='{desc}{percentage:3.0f}%|{bar:100}'), 1):
                if self.other_inputs:
                    images, other_inputs, steering_labels, act_value_labels = data
                    other_inputs = other_inputs.to(self.device)
                else:
                    images, steering_labels, act_value_labels = data
                images = self.normalize_image(images.to(self.device, non_blocking=True))
                steering_labels = steering_labels.to(self.device, non_blocking=True)
                act_value_labels = act_value_labels.to(self.device, non_blocking=True)
                if self.other_inputs:  
                    steering_prediction, act_value_prediction = self.model(images, other_inputs)
                else:
                    steering_prediction, act_value_prediction = self.model(images)
                steering_loss = self.criterion(steering_prediction, steering_labels)
                act_value_loss = self.criterion(act_value_prediction, act_value_labels)
                loss = self.steering_weight * steering_loss + self.act_value_weight * act_value_loss
                losses["steering"].append(steering_loss)
                losses["act_value"].append(act_value_loss)
                losses["loss"].append(loss)
        eval_steering_loss = sum(losses["steering"]) / batch_no
        eval_act_value_loss = sum(losses["act_value"]) / batch_no
        eval_loss = sum(losses["loss"]) / batch_no
        return eval_loss, eval_steering_loss, eval_act_value_loss

    @staticmethod
    def normalize_image(array):
        # Making values between [0, 1]
        return array / 255

    def save_model(self):
        model_save_path = os.path.join(os.path.expanduser('~'), "e2e-driver", "models")
        torch.save(self.model.state_dict(), os.path.join(model_save_path, self.model_name + ".pt"))
        script_cell = torch.jit.script(self.model)
        torch.jit.save(script_cell, os.path.join(model_save_path, self.model_name + ".jit"))
        logger.info(f"Saved the model to {os.path.join(model_save_path, self.model_name)}\n")


if __name__ == "__main__":
    args = docopt(__doc__)
    data_dirs = args["<data_dirs>"]
    test_dirs = args["--test_dirs"]
    model_path = args["--model"]
    model_save_name = args["--name"]
    if not model_save_name:
        model_save_name = "model"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    main()