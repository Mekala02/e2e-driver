#!/usr/bin/env bash

L4T_VERSION="35.1.0"
OPENCV_URL="https://nvidia.box.com/shared/static/2hssa5g3v28ozvo3tc3qwxmn78yerca9.gz"
OPENCV_DEB="OpenCV-4.5.0-aarch64.tar.gz"
BASE_IMAGE="nvcr.io/nvidia/l4t-jetpack:r35.1.0"

PYTHON3_VERSION="3.8"


cd ..
echo "Building $CONTAINER container..."
sudo docker build --network=host -t e2e-driver -f Dockerfile.e2edriver \
		--build-arg BASE_IMAGE=$BASE_IMAGE \
		--build-arg PYTORCH_IMAGE=nvcr.io/nvidia/l4t-pytorch:r$L4T_VERSION-pth1.11-py3 \
		--build-arg TENSORFLOW_IMAGE=nvcr.io/nvidia/l4t-tensorflow:r$L4T_VERSION-tf2.9-py3 \
		--build-arg PYTHON3_VERSION=$PYTHON3_VERSION \
		--build-arg OPENCV_URL=$OPENCV_URL \
		--build-arg OPENCV_DEB=$OPENCV_DEB \
        .