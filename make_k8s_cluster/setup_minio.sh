# Install minio using ceph to back our storage. Deploy on the x86 because we don't have the rbd kernel module on the ARM nodes. Also we want to save the arm nodes for compute.
helm install --namespace minio --generate-name minio/minio --set   persistence.storageClass=rook-ceph-block,nodeSelector."beta\\.kubernetes\\.io/arch"=amd64
# Do a helm ls and find the deployment name name
deployment_name=$(helm ls -n minio | cut -f 1 | tail -n 1)
ACCESS_KEY=$(kubectl get secret -n minio "$deployment_name" -o jsonpath="{.data.accesskey}" | base64 --decode); SECRET_KEY=$(kubectl get secret -n minio "$deployment_name" -o jsonpath="{.data.secretkey}" | base64 --decode)
# Defaults are "YOURACCESSKEY" and "YOURSECRETKEY"
mc alias set "${deployment_name}-local" http://localhost:9000 "$ACCESS_KEY" "$SECRET_KEY" --api s3v4
mc ls "${deployment_name}-local"
mc mb "${deployment_name}-local"://dask-test
