#!/usr/bin/env bash
L4T_VERSION="35.1.0"
OPENCV_URL="https://nvidia.box.com/shared/static/2hssa5g3v28ozvo3tc3qwxmn78yerca9.gz"
OPENCV_DEB="OpenCV-4.5.0-aarch64.tar.gz"
BASE_IMAGE="nvcr.io/nvidia/l4t-jetpack:r35.1.0"

tensorflow_url="https://developer.download.nvidia.com/compute/redist/jp/v50/tensorflow/tensorflow-2.9.1+nv22.06-cp38-cp38-linux_aarch64.whl"
tensorflow_whl="tensorflow-2.9.1+nv22.06-cp38-cp38-linux_aarch64.whl"
tensorflow_tag="l4t-tensorflow:r$L4T_VERSION-tf2.9-py3"
protobuf_version="3.20.1"

CONTAINER=$tensorflow_tag

#sudo cp cuda-devel.csv /etc/nvidia-container-runtime/host-files-for-container.d/
echo "building TensorFlow $tensorflow_whl, $tensorflow_tag"
echo "Building $CONTAINER container..."

sudo docker build --network=host -t $CONTAINER -f Dockerfile.tensorflow \
    --build-arg BASE_IMAGE=$BASE_IMAGE \
    --build-arg TENSORFLOW_URL=$tensorflow_url \
    --build-arg TENSORFLOW_WHL=$tensorflow_whl \
    --build-arg PROTOBUF_VERSION=$protobuf_version \
    --build-arg OPENCV_URL=$OPENCV_URL \
    --build-arg OPENCV_DEB=$OPENCV_DEB  \
    .

echo "done building TensorFlow $tensorflow_whl, $tensorflow_tag"