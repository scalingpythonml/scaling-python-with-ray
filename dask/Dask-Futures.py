#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dask
from dask_kubernetes import KubeCluster
import numpy as np
import time
import timeit


# In[45]:


#tag::launching_futures[]
from dask.distributed import Client
client = Client()

def slow(x):
    time.sleep(3*x)
    return 3*x

slow_future = client.submit(slow, 1)
slow_futures = client.map(slow, range(1, 5))
#end::launching_futures[]


# In[46]:


#tag::delayed_vs_future_future_faster[]
slow_future = client.submit(slow, 1)
slow_delayed = dask.delayed(slow)(1)
# Pretend we do some other work here
time.sleep(1)
future_time = timeit.timeit(lambda: slow_future.result(), number=1)
delayed_time = timeit.timeit(lambda: dask.compute(slow_delayed), number=1)
print(f"So as you can see by the future time {future_time} v.s. {delayed_time} the future starts running right away.")
#end::delayed_vs_future_future_faster[]


# In[47]:


#tag::understanding_futures_lifecycle[]
myfuture = client.submit(slow, 5) # Starts running
myfuture = None # future may be GCd and then stop since there are no other references

myfuture = client.submit(slow, 5) # Starts running
del myfuture # future may be GCd and then stop since there are no other references

myfuture = client.submit(slow, 5) # Starts running
myfuture.cancel() # Future stops running, any other references point to cancelled future
#end::understanding_futures_lifecycle[]


# In[48]:


myfuture


# In[49]:


del myfuture


# In[50]:


myfuture = client.submit(slow, 5) # Starts running


# In[51]:


myfuture2 = myfuture


# In[52]:


del myfuture


# In[53]:


myfuture2


# In[54]:


#tag::fire_and_forget[]
from dask.distributed import fire_and_forget

def process_something(x):
    """
    Process x but don't wait for any response.
    """
    myfuture = client.submit(slow, x)
    fire_and_forget(myfuture)
    # If we didn't use fire and forget the future would be cancelled on return
    return True

process_something(10)
#end::fire_and_forget[]


# In[ ]:


#tag::fire_and_forget2[]
from dask.distributed import fire_and_forget

def do_some_io(data):
    """
    Do some io we don't need to block on :)
    """
    import requests
    return requests.get('https://httpbin.org/get', params=data)
    
def business_logic():
    # Make a future, but we don't really care about it's result, just that it happens
    future = client.submit(do_some_io, {"timbit": "awesome"})
    fire_and_forget(future)
    
business_logic()
#end::fire_and_forget2[]


# In[105]:


#tag::get_result[]
future = client.submit(do_some_io, {"timbit": "awesome"})
future.result()
#end::get_result[]


# In[55]:


things = list(range(10))
things.sort(reverse=True)
futures = client.map(slow, things)


# In[56]:


#tag::get_seq[]
for f in futures:
    time.sleep(2) # Business numbers logic
    print(f.result())
#end::get_seq[]


# In[57]:


futures = client.map(slow, things)


# In[58]:


#tag::as_completed[]
from dask.distributed import as_completed

for f in as_completed(futures):
    time.sleep(2) # Business numbers logic
    print(f.result())
#end::as_completed[]


# In[59]:


futures


# In[60]:


#tag::nested[]
from dask.distributed import get_client

def nested(x):
    client = get_client() # The client is serializable so we use get_client
    futures = client.map(slow, range(0, x))
    r = 0
    for f in as_completed(futures):
        r = r + f.result()
    return r

f = client.submit(nested, 3)
f.result()
#end::nested[]


# In[94]:


futures = client.map(slow, range(0, 30))


# In[95]:


#tag::time_limit_first[]
from dask.distributed import wait
from dask.distributed.client import FIRST_COMPLETED

# Will throw an exception if no future completes in time
# If it does not throw the result has two lists:
# The done list may return between one and all futures.
# The not_done list may contain zero or more futures.
finished = wait(futures, 1, return_when=FIRST_COMPLETED)

# Process the returned futures
for f in finished.done:
    print(f.result())
    
# Cancel the futures we don't need
for f in finished.not_done:
    f.cancel()
#end::time_limit_first[]


# In[98]:


futures = client.map(slow, range(0, 30))
#tag::time_limit_some[]
max_wait = 10
start = time.time()

while len(futures) > 0 and time.time() - start < max_wait:
    try:
        finished = wait(futures, 1, return_when=FIRST_COMPLETED)
        for f in finished.done:
            print(f.result())
        futures = finished.not_done
    except TimeoutError:
        True # No future finished in this cycle

# Cancel any remaining futures
for f in futures:  
    f.cancel()
#end::time_limit_some[]


# In[76]:


#tag::time_limit_all[]
# You can also wait for all of the futures:
finished = wait(futures, 10) # Throws an exception if not all finished by timeout
#end::time_limit_all[]


# In[89]:


type(finished.done)


# In[103]:





# In[ ]:




