#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dask
from dask_kubernetes import KubeCluster
import numpy as np


# In[2]:


# Specify a remote deployment using a load blanacer
dask.config.set({"kubernetes.scheduler-service-type": "LoadBalancer"})


# In[3]:


cluster = KubeCluster.from_yaml('worker-spec.yaml', namespace='dask', deploy_mode='remote')


# In[4]:


cluster.adapt(minimum=1, maximum=10)


# In[9]:


# Example usage
from dask.distributed import Client
import dask.array as da

# Connect Dask to the cluster
client = Client(cluster)


# In[10]:


client.scheduler_comm.comm.handshake_info()


# In[11]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# So now we know the cluster is doing ok :)

# In[16]:


class Counter:
    """ A simple class to manage an incrementing counter """
    n = 0

    def __init__(self):
        self.n = 0

    def increment(self):
        self.n += 1
        return self.n

    def add(self, x):
        self.n += x
        return self.n
    
    def value(self):
        return self.n


future = client.submit(Counter, actor=True)  # Create a Counter on a worker
counter = future.result()     


# In[17]:


counter


# In[22]:


counter.increment()


# In[23]:


counter.value().result()


# In[57]:


import dask.bag as db
b = db.from_sequence(range(1,100), npartitions=10)
import time


# In[64]:


def inc(x):
    time.sleep(x)
    f = counter.add(x)
    # Note: the counter ( above ) is serelizable, however the future we get back from it is not
    # this is likely because the future contains a network connection to the actor, so we don't return
    # that future. If we wanted to we could also block on f's value here.
    return x
j = b.map(inc)
j


# In[59]:


f = j.to_delayed()
f


# In[62]:


c = client
c.submit(*f)


# In[63]:


counter.value().result()


# In[ ]:


counter.value().result()


# In[ ]:


counter.value().result()


# In[ ]:


f[0]


# In[ ]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# In[ ]:




