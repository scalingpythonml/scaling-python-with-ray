#!/bin/bash
#tag::add_ray_chart[]
git clone git@github.com:ray-project/ray.git
pushd ray/deploy/charts
#end::add_ray_chart[]
# Deploy operator
#tag::deploy_operator[]
helm install ray-operator  --set operatorOnly=true ./ray
#end::deploy_operator[]
#tag::deploy_cluster[]
helm install gpu-cluster -n ray --create-namespace --set clusterOnly=true -f ~/repos/scalingpythonml/ray/k8s/helm_config_selector.yaml ./ray
#end::deploy_cluster[]
