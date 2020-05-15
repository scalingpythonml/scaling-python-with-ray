#!/bin/bash
pushd /rook/rook/cluster/examples/kubernetes/ceph
kubectl create -f common.yaml
kubectl create -f rook_operator_arm64.yaml
kubectl create -f rook_cluster.yaml
