import ray
from time import sleep

# Import placement group APIs.
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group
)

# Init ray.
ray.init()


@ray.remote(num_cpus=2)
def remote_function():
    sleep(2)
    return 1

# Print cluster state
print(ray.cluster_resources())
print(ray.available_resources())

# Create a placement group.
cpu_bundle = {"CPU": 3}
pg = placement_group([cpu_bundle])
ray.get(pg.ready())
print(placement_group_table(pg))
print(ray.available_resources())

handle = remote_function.remote()
sleep(1)
print(ray.available_resources())
print(ray.get(handle))
sleep(1)
print(ray.available_resources())

handle = remote_function.options(placement_group=pg).remote()
sleep(1)
print(ray.available_resources())
print(ray.get(handle))
sleep(1)
print(ray.available_resources())

# Delete placement group. This API is asynchronous.
remove_placement_group(pg)
# Wait until placement group is killed.
sleep(1)
# Check the placement group has died.
print(placement_group_table(pg))
print(ray.available_resources())