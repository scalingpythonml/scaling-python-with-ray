from collections import Counter
import sys
import time
import ray
""" Run this script locally to execute a Ray program on your Ray cluster on
Kubernetes.
Before running this script, you must port-forward from the local host to
the relevant Kubernetes head service e.g.
kubectl -n ray port-forward service/example-cluster-ray-head 10001:10001.
Set the constant LOCAL_PORT below to the local port being forwarded.
"""

@ray.remote
def gethostname(x):
    import platform
    import time
    time.sleep(0.01)
    return x + (platform.node(), )


def wait_for_nodes(expected):
    # Wait for all nodes to join the cluster.
    while True:
        resources = ray.cluster_resources()
        node_keys = [key for key in resources if "node" in key]
        num_nodes = sum(resources[node_key] for node_key in node_keys)
        if num_nodes < expected:
            print("{} nodes have joined so far, waiting for {} more.".format(
                num_nodes, expected - num_nodes))
            sys.stdout.flush()
            time.sleep(1)
        else:
            break


def main():
    wait_for_nodes(1)

    # Check that objects can be transferred from each node to each other node.
    for i in range(10):
        print("Iteration {}".format(i))
        results = [
            gethostname.remote(gethostname.remote(())) for _ in range(100)
        ]
        print(Counter(ray.get(results)))
        sys.stdout.flush()

    print("Success!")
    sys.stdout.flush()


if __name__ == "__main__":
    print(f'Using Ray version {ray.__version__}')
    ray.init(address='ray://52.118.80.225:10001')
    main()