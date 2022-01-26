#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ray
import time


# In[ ]:


# Connect to the ray cluster
CLUSTER_NAME = "gpu-cluster"
NAMESPACE = "ray"
PORT=10001
# The dns name is based off of the service name which is [cluster]-ray-head & namespace
dns_name = f"{CLUSTER_NAME}-ray-head.{NAMESPACE}.svc"
ray.util.connect(f"{dns_name}:{PORT}")


# In[ ]:


#tag::placement_group_imports[]
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group
)
#end::placement_group_imports[]


# In[ ]:


#tag::mixed_placement_group[]
# Create a placement group.
cpu_bundle = {"CPU": 1}
gpu_bundle = {"GPU": 1}
pg = placement_group([cpu_bundle, gpu_bundle])
ray.get(pg.ready())
print(placement_group_table(pg))
print(ray.available_resources())
#end::mixed_placement_group[]


# In[ ]:


@ray.remote
def remote_fun(x):
    return x


# In[ ]:


ray.get(pg.ready())
print(placement_group_table(pg))
print(ray.available_resources())

handle = remote_fun.options(placement_group=pg).remote(1)
print(ray.available_resources())
print(ray.get(handle))

# Delete placement group. This API is asynchronous.
remove_placement_group(pg)
# Wait until placement group is killed.
time.sleep(1)
# Check the placement group has died.
print(placement_group_table(pg))
print(ray.available_resources())


# In[ ]:




