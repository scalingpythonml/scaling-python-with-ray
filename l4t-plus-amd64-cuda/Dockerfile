# We need to use l4t for the arm image but it's not cross-build so use regular cuda for amd64

FROM ubuntu:18.04 as base

FROM nvidia/cuda:10.2-devel-ubuntu18.04 AS base-amd64
ENV NVARCH x86_64

#FROM nvcr.io/nvidia/l4t-base:r32.6.1 as base-arm64
FROM mdegans/l4t-base:xavier as base-arm64
#FROM nvcr.io/nvidia/l4t-tensorflow:r32.7.1-tf2.7-py3 as base-arm64

ENV NVARCH sbsa
# See https://forums.developer.nvidia.com/t/numpy-throwing-illegal-instruction-core-dumped-error/184030
ENV OPENBLAS_CORETYPE ARMV8

RUN mv /etc/apt/sources.list.d/nvidia-l4t-apt-source.list /etc/apt/ || echo "k"
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates
RUN mv /etc/apt/nvidia-l4t-apt-source.list /etc/apt/sources.list.d || echo "k..."
RUN apt-get update && apt-get upgrade -y 


FROM base-${TARGETARCH}
ARG TARGETARCH

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get upgrade -y
RUN apt-get install -y ubuntu-release-upgrader-core
RUN do-release-upgrade -f DistUpgradeViewNonInteractive

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:ubuntu-toolchain-r/ppa
RUN add-apt-repository ppa:ubuntu-toolchain-r/test
#RUN add-apt-repository ppa:ubuntu-toolchain-r/glibc
# We need gcc 9 for Ray, but it's the default in 20.04
#RUN add-apt-repository ppa:savoury1/gcc-defaults-9
RUN apt-get update
RUN apt-get install -y strace gcc-9 g++-9 strace g++ gcc build-essential
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9 --slave /usr/bin/gcov gcov /usr/bin/gcov-9
RUN gcc -v


COPY setup.sh .
RUN ./setup.sh
