#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from collections import Counter
import sys
import time
import ray


# In[ ]:


# Connect to the ray cluster
CLUSTER_NAME = "gpu-cluster"
NAMESPACE = "ray"
PORT=10001
# The dns name is based off of the service name which is [cluster]-ray-head & namespace
dns_name = f"{CLUSTER_NAME}-ray-head.{NAMESPACE}.svc"
ray.util.connect(f"{dns_name}:{PORT}")


# In[ ]:




