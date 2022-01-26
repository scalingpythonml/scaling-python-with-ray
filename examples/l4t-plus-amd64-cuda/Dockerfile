# We need to use l4t for the arm image but it's not cross-build so use regular cuda for amd64

FROM ubuntu:18.04 as base

FROM nvidia/cuda:10.2-devel-ubuntu18.04 AS base-amd64
ENV NVARCH x86_64

FROM nvcr.io/nvidia/l4t-base:r32.6.1 as base-arm64
#FROM mdegans/l4t-base:xavier as base-arm64
ENV NVARCH sbsa
# See https://forums.developer.nvidia.com/t/numpy-throwing-illegal-instruction-core-dumped-error/184030
ENV OPENBLAS_CORETYPE ARMV8

RUN mv /etc/apt/sources.list.d/nvidia-l4t-apt-source.list /etc/apt/ || echo "k"
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates
RUN mv /etc/apt/nvidia-l4t-apt-source.list /etc/apt/sources.list.d || echo "k..."

FROM base-${TARGETARCH}
ARG TARGETARCH

COPY setup.sh .
RUN ./setup.sh
