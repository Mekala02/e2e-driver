"""
Usage:
    convert_to_tensorrt.py  <model_path>

Options:
  -h --help     Show this screen.
"""
from docopt import docopt
import os
import torch
from torch2trt import torch2trt
from networks import Linear

args = docopt(__doc__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = args["<model_path>"]
model = Linear(in_channels=3).to(device)
model.load_state_dict(torch.load(model_path))
model.eval()

# create example data
x = torch.randn((64, 3, 120, 160)).cuda(device=device)

# convert to TensorRT feeding sample data as input
model_trt = torch2trt(model, [x])
head, tail = os.path.split(model_path)
name, extension = os.path.splitext(tail)
# model_save_path = os.path.join('./models', "model_trt.pth")
torch.save(model_trt.state_dict(), os.path.join(head , name + "_trt" + extension))