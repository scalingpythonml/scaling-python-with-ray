#!/bin/bash
pushd containers
./build.sh
popd
#tag::setupsa[]
kubectl create serviceaccount -n jhub spark
kubectl create namespace spark
kubectl create rolebinding spark-role --clusterrole=edit --serviceaccount=jhub:spark --namespace=spark
# We can't override SA in the launcher on per-container basis, so since I've already got a dask SA.
kubectl create rolebinding spark-role-to-dask-acc --clusterrole=edit --serviceaccount=jhub:dask --namespace=spark
#end::setupsa[]
# Create a service for the executors to connect back to the driver on the notebook
#tag::setup_service[]
kubectl apply -n jhub -f driver-service.yaml
#end::setup_service[]
