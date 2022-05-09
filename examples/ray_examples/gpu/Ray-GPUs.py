#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Ray GPUs local
#tag::start-ray-gpu[]
import ray
ray.init(num_cpus=20, num_gpus=1)
#end::start-ray-gpu[]


# In[ ]:


#tag::remote_gpu[]
# Request a full GPU, like CPUs we can request fractional
@ray.remote(num_gpus=1)
def do_serious_work():
#end::remote_gpu[]
    return hi


# In[ ]:


#tag::remote_gpu[]
# Restart entire worker after each call
@ray.remote(num_gpus=1, max_calls=1)
def do_serious_work():
#end::remote_gpu[]
    return hi


# In[ ]:


#tag::gpu_fallback[]

# Function that requests a GPU
@ray.remote(num_gpus=1)
def do_i_have_gpus():
    return True

# Give it at most 4 minutes to see if we can get a GPU
# We want to give the auto-scaler some time to see if it can spin up
# a GPU node for us.
futures = [do_i_have_gpus.remote()]
ready_futures, rest_futures = ray.wait(futures, timeout=240)

resources = {"num_cpus": 1}
# If we have a ready future then we have a GPU node in our cluster
if ready_futures:
    resources["num_gpus"] =1

# "splat" the resources
@ray.remote(** resources)
def optional_gpu_task():
#end::gpu_fallback[]
    return "k"


# In[ ]:


not ready_futures


# In[ ]:


resources


# In[ ]:




