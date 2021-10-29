#!/bin/bash
export SCALING_PYTHON_ML_EXAMPLES_PATH=$(realpath "$(dirname "$0")")
#tag::add_ray_chart[]
git clone git@github.com:ray-project/ray.git
pushd ray/deploy/charts
#end::add_ray_chart[]
# Deploy operator
#tag::deploy_operator[]
helm install ray-operator  --set operatorOnly=true ./ray
#end::deploy_operator[]
#tag::deploy_cluster[]
helm install gpu-cluster -n ray --create-namespace --set clusterOnly=true -f ${SCALING_PYTHON_ML_EXAMPLES_PATH}/ray/installRay/helm/helm_config_selector.yaml ./ray
#end::deploy_cluster[]
