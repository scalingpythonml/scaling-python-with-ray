#!/usr/bin/env python
# coding: utf-8

# In[2]:


from dask_kubernetes import KubeCluster


# In[4]:


# Initial attempt at creation (also failed do to networking)
#tag::create_in_namespace[]
cluster = KubeCluster.from_yaml('worker-spec.yaml')
#end::create_in_namespace[]


# In[5]:


# This is the one where it failed because I was running it outside a cluster and it could not communicate
#tag::create_in_namespace[]
cluster = KubeCluster.from_yaml('worker-spec.yaml', namespace='dask')
#end::create_in_namespace[]


# In[3]:


cluster.adapt(minimum=1, maximum=100)


# In[5]:


# Example usage
from dask.distributed import Client
import dask.array as da

# Connect Dask to the cluster
client = Client(cluster)


# In[6]:


client.scheduler_comm.comm.handshake_info()


# In[7]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# In[ ]:




