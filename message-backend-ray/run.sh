#!/bin/bash
source .settings.sh
pod_name=$(kubectl get pod -n ray  -l ray-cluster-name=spacebeaver,ray-node-type=head -o name)
set -x
# The job API is changing in 3.0 and it's not documented yet so use legacy APIs for now
kubectl port-forward -n ray ${pod_name} 10001:10001 &
kubectl port-forward -n ray ${pod_name} 8265:8265 &
sleep 2 # Wait for forward, kind of hacky I know.
export RAY_ADDRESS="http://localhost:8625"
export RAY_HEAD_ADDRESS="ray://localhost:10001"
export DJANGO_CONFIGURATION=${DJANGO_CONFIGURATION:-Runtime}
export __ENV__=${__ENV__:-Runtime}
export ENVIRONMENT=${ENVIRONMENT:-production}
export DOMAIN=spacebeaver.com
export SECRET_KEY=thisisnotverysecret
# Run "new", note in 1.9 it's ray job submit
#ray job submit -runtime-env-json '{"working_dir": "./", "pip": 
#  ["protobuf<4.0.0,>=3.15.3",
#   "aiosmtpd",
#   "Django>=3.2.14",
#   "psycopg2-binary"],
#  env_vars: {
#    "mail_server": "$mail_server",
#    "mail_username": "$mail_username",
#    "mail_password": "$mail_password",
#    "swarm_username": "$swarm_password"}
#}' -- 'python ./messaging/main.py'
# Run "classic"
python ./messaging/main.py --ray-head ${RAY_HEAD_ADDRESS}
