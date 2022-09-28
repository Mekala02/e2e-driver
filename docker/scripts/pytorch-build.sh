#!/usr/bin/env bash

L4T_VERSION="35.1.0"
OPENCV_URL="https://nvidia.box.com/shared/static/2hssa5g3v28ozvo3tc3qwxmn78yerca9.gz"
OPENCV_DEB="OpenCV-4.5.0-aarch64.tar.gz"
BASE_IMAGE="nvcr.io/nvidia/l4t-jetpack:r35.1.0"

pytorch_url="https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl"
pytorch_whl="torch-1.11.0-cp38-cp38-linux_aarch64.whl"
pytorch_tag="l4t-pytorch:r$L4T_VERSION-pth1.11-py3"

vision_version="v0.12.0"
audio_version="v0.11.0"
cuda_arch_list="7.2;8.7"

CONTAINER=$pytorch_tag

cd ..
echo "building PyTorch $pytorch_whl, torchvision $vision_version, torchaudio $audio_version, cuda arch $cuda_arch_list"
echo "Building $CONTAINER container..."

sudo docker build --network=host -t $CONTAINER -f Dockerfile.pytorch\
			--build-arg BASE_IMAGE=$BASE_IMAGE \
			--build-arg PYTORCH_URL=$pytorch_url \
			--build-arg PYTORCH_WHL=$pytorch_whl \
			--build-arg TORCHVISION_VERSION=$vision_version \
			--build-arg TORCHAUDIO_VERSION=$audio_version \
			--build-arg TORCH_CUDA_ARCH_LIST=$cuda_arch_list \
			--build-arg OPENCV_URL=$OPENCV_URL \
			--build-arg OPENCV_DEB=$OPENCV_DEB \
            .

echo "done building PyTorch $pytorch_whl, torchvision $vision_version, torchaudio $audio_version, cuda arch $cuda_arch_list"