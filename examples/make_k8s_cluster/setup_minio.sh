# Install minio using ceph to back our storage. Deploy on the x86 because we don't have the rbd kernel module on the ARM nodes. Also we want to save the arm nodes for compute.
set -ex
helm repo update
helm status -n minio minio || helm install minio minio/minio --namespace minio --set   nodeSelector."beta\\.kubernetes\\.io/arch"=amd64 
# Do a helm ls and find the deployment name name
deployment_name=$(helm ls -n minio | cut -f 1 | tail -n 1)
sleep 5
export MINIO_POD_NAME=$(kubectl get pods --namespace minio -l "release=minio" -o jsonpath="{.items[0].metadata.name}")
sleep 5
kubectl port-forward $MINIO_POD_NAME 9000 --namespace minio &
ACCESS_KEY=$(kubectl get secret -n minio "$deployment_name" -o jsonpath="{.data.accesskey}" | base64 --decode); SECRET_KEY=$(kubectl get secret -n minio "$deployment_name" -o jsonpath="{.data.secretkey}" | base64 --decode)
# Defaults are "YOURACCESSKEY" and "YOURSECRETKEY"
mc alias set "${deployment_name}-local" http://localhost:9000 "$ACCESS_KEY" "$SECRET_KEY" --api s3v4
mc ls "${deployment_name}-local"
mc mb "${deployment_name}-local"/dask-test
mc mb "${deployment_name}-local"/spark-test
mc mb "${deployment_name}-local"/spark-extra
# Expire shuffle files after 2 days. Note this _might_ not work in which case do a cleanup on your own.
mc ilm import "${deployment_name}-local"/spark-extra <<EOF
{
    "Rules": [
        {
            "Expiration": {
                "Days": 2
            },
            "ID": "TempUploads",
            "Status": "Enabled"
        }
    ]
}
EOF
