"""
Usage:
    convert_to_tensorrt.py  <data_dir>

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
model_path = args["<data_dir>"]
model = Linear(in_channels=3).to(device)
model.load_state_dict(torch.load(model_path))
model.eval()

# create example data
x = torch.ones((1, 3, 376, 672)).cuda(device=device)

# convert to TensorRT feeding sample data as input
model_trt = torch2trt(model, [x], fp16_mode=True)

model_save_path = os.path.join('./models', "model_trt.pth")
torch.save(model_trt.state_dict(), model_save_path)