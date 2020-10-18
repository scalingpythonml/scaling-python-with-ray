#!/bin/bash
pushd /rook/cluster/examples/kubernetes/ceph
kubectl create -f common.yaml
kubectl create -f rook_operator_arm64.yaml
kubectl create -f rook_cluster.yaml
kubectl create -f ./csi/rbd/storageclass.yaml
