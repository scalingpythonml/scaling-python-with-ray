#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dask
from dask_kubernetes import KubeCluster
import numpy as np


# In[2]:


# Specify a remote deployment using a load blanacer
dask.config.set({"kubernetes.scheduler-service-type": "LoadBalancer"})


# In[4]:


cluster = KubeCluster.from_yaml('worker-spec.yaml', namespace='dask', deploy_mode='remote')


# In[5]:


cluster.adapt(minimum=1, maximum=100)


# In[6]:


# Example usage
from dask.distributed import Client
import dask.array as da

# Connect Dask to the cluster
client = Client(cluster)


# In[7]:


client.scheduler_comm.comm.handshake_info()


# In[8]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# In[9]:


print(array.mean().compute())


# In[10]:


print(array.sum().compute())


# In[13]:


dir(array)


# In[18]:


np.take(array, indices=[0, 10]).sum().compute()


# In[15]:





# In[ ]:




