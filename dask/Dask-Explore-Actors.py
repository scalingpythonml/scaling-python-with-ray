#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dask
from dask_kubernetes import KubeCluster
import numpy as np


# In[ ]:





# In[ ]:


import dask
from dask.distributed import Client
from dask_kubernetes import KubeCluster, make_pod_spec
dask.config.set({"kubernetes.scheduler-service-type": "LoadBalancer"})
worker_template = make_pod_spec(image='holdenk/dask:latest',
                         memory_limit='8G', memory_request='8G',
                         cpu_limit=1, cpu_request=1)
scheduler_template = make_pod_spec(image='holdenk/dask:latest',
                         memory_limit='4G', memory_request='4G',
                         cpu_limit=1, cpu_request=1)
cluster = KubeCluster(pod_template = worker_template, scheduler_pod_template = scheduler_template)
cluster.adapt()    # or create and destroy workers dynamically based on workload
from dask.distributed import Client
client = Client(cluster)


# In[ ]:


cluster.adapt(minimum=1, maximum=10)


# In[ ]:


client.scheduler_comm.comm.handshake_info()


# In[ ]:


import dask.array as da


# In[ ]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# So now we know the cluster is doing ok :)

# In[ ]:


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


# In[ ]:


counter


# In[ ]:


counter.increment()


# In[ ]:


counter.value().result()


# In[ ]:


import dask.bag as db
b = db.from_sequence(range(0, 10))


# In[ ]:


#tag::result_future_not_ser[]
def inc(x):
    import time
    time.sleep(x)
    f = counter.add(x)
    # Note: the actor (in this case `counter`) is serelizable, however the future we get back from it is not
    # this is likely because the future contains a network connection to the actor, so need to get it's
    # concrete value here. If we don't need the value you can avoid blocking and it will still execute.
    return f.result()
#end::result_future_not_ser[]


# In[ ]:


c = client
futures = list(map(lambda x: c.submit(inc, x), range(10)))


# In[ ]:


futures


# In[ ]:


counter.value().result()


# In[ ]:


futures[5].result()


# In[ ]:


counter.value().result()


# In[ ]:


#tag::make_account[]
class BankAccount:
    """ A bank account actor (similar to counter but with + and -)"""

    # 42 is a good start
    def __init__(self, balance=42.0):
        self._balance = balance

    def deposit(self, amount):
        if amount < 0:
            raise Exception("Can not deposit negative amount")
        self._balance += amount
        return self._balance

    def withdrawl(self, amount):
        if amount > self._balance:
            raise Exception("Please deposit more money first.")
        self._balance -= amount
        return self._balance

    def balance(self):
        return self._balance


account_future = client.submit(BankAccount, actor=True)  # Create a BankAccount on a worker
account = account_future.result()
#end::make_account[]


# In[ ]:


#tag::use_account[]
# Non-blocking
balance_future = account.balance()
# Blocks
balance = balance_future.result()
try:
    f = account.withdrawl(100)
    f.result() # throws an exception
except Exception as e:
    print(e)
#end::use_account[]


# In[ ]:


f = account.withdrawl(1)


# In[ ]:


f.result()


# In[ ]:




