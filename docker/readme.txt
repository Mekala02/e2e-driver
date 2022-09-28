You don't need to build containers yourself, you can pull them with following commands:

# For Pytorch
sudo docker pull nvcr.io/nvidia/l4t-pytorch:r35.1.0-pth1.11-py3

# For Tensorflow
sudo docker pull nvcr.io/nvidia/l4t-tensorflow:r35.1.0-tf2.9-py3

# For Zed SDK
sudo docker pull stereolabs/zed:3.7-devel-l4t-r35.1

# For e2e-driver (This contains Pytorch, Tensorflow and Zed Sdk)
sudo docker pull mekala02/e2e-driver