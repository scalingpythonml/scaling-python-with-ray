#!/bin/bash
pushd /rook/rook/cluster/examples/kubernetes/ceph
kubectl create -f common.yaml
kubectl create -f operator.yaml
kubectl create -f rook_cluster.yaml
