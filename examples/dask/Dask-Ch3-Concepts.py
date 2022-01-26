#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dask
# Dask multithreading is only suited for mostly non-Python code (like pandas, numpy, etc.)
#tag::threads[]
dask.config.set(scheduler='threads')
#end::threads[]
#tag::process[]
dask.config.set(scheduler='processes')
#end::process[]
#tag::dask_use_forkserver[]
dask.config.set({"multiprocessing.context": "forkserver", "scheduler": "processes"})
#end::dask_use_forkserver[]


# In[ ]:


#tag::make_dask_k8s_client[]
import dask
from dask.distributed import Client
from dask_kubernetes import KubeCluster, make_pod_spec
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
#end::make_dask_k8s_client[]


# In[ ]:


#tag::fib_task_hello_world[]
def dask_fib(x):
    if x < 2:
        return x
    a = dask.delayed(dask_fib(x-1))
    b = dask.delayed(dask_fib(x-2))
    c, d = dask.compute(a, b) # Compute in parallel
    return c + d

def seq_fib(x):
    if x < 2:
        return x
    return seq_fib(x-1) + seq_fib(x-2)

import functools
@functools.lru_cache
def fib(x):
    if x < 2:
        return x
    return fib(x-1) + fib(x-2)

import timeit
seq_time = timeit.timeit(lambda: seq_fib(14), number=1)
dask_time = timeit.timeit(lambda: dask_fib(14), number=1)
memoized_time = timeit.timeit(lambda: fib(14), number=1)
print("In sequence {}, in parallel {}, memoized".format(seq_time, dask_time, memoized_time))
#end::fib_task_hello_world[]


# In[ ]:




