#!/bin/bash

# Get our versions to match as much as possible easily.
sudo /opt/conda/bin/conda install -c conda-forge --all --yes     python==3.8     cytoolz     dask==2.28.0     lz4     nomkl     numpy     pandas     tini     scikit-build     python-blosc


# Create a namespace & SA & permissions.
#kubectl create namespace dask
#kubectl create serviceaccount dask --namespace dask
#kubectl apply -f setup.yaml
#kubectl create rolebinding dask-sa-binding --namespace dask --role=daskKubernetes --user=dask:dask

# Set up SSL trust of the k3s hosts?
scp root@k8s-leader.local:/var/lib/rancher/k3s/agent/client-ca.crt ~/k3s-ca.crt
export REQUESTS_CA_BUNDLE=~/k3s-ca.crt
