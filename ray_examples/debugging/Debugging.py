#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ray
from multiprocessing import Pool


# In[2]:


#tag::bad_ser_example[]
pool = Pool(5)

def special_business(x):
    def inc(y):
        return y + x
    return pool.map(inc, range(0, x))
ray.util.inspect_serializability(special_business)
#end::bad_ser_example[]


# In[15]:


#tag::ex_pydev_charm[]
@ray.remote
class Bloop():
    
    def __init__(self, dev_host):
        import pydevd_pycharm
        # Requires ability to connect to dev from prod.
        try:
            pydevd_pycharm.settrace(dev_host, port=7779, stdoutToServer=True, stderrToServer=True)
        except ConnectionRefusedError:
            print("Skipping debug")
            pass
    
    def dothing(x):
        return x + 1
#end::ex_pydev_charm[]


# In[16]:


bloop_actor = Bloop.remote("localhost")

