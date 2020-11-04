#!/bin/bash

# Get our versions to match as much as possible easily.
#tag::setup_conda[]
sudo /opt/conda/bin/conda install -c conda-forge --all --yes mamba
mamba install --yes python==3.8.6 cytoolz dask==2.30.0 dask-core==2.30.0 lz4 numpy==1.19.2 pandas tini \
      scikit-build python-blosc=1.9.2 pyzmq s3fs gcsfs dropboxdrivefs requests dropbox paramiko adlfs \
      pygit2 pyarrow bokeh aiottp==3.7.1 llvmlite numba fastparquet
#end::setup_conda[]

# Create a namespace & SA & permissions.
#tag::setup_namespace[]
kubectl create namespace dask
kubectl create serviceaccount dask --namespace dask
kubectl apply -f setup.yaml
kubectl create rolebinding dask-sa-binding --namespace dask --role=daskKubernetes --user=dask:dask
#end::setup_namespace[]

# Set up SSL trust of the k3s hosts?
scp root@k8s-leader.local:/var/lib/rancher/k3s/agent/client-ca.crt ~/k3s-ca.crt
export REQUESTS_CA_BUNDLE=~/k3s-ca.crt
