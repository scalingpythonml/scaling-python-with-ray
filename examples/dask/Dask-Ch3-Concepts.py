#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dask
import numpy as np
import numpy.typing as npt
from typing import *
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
                         cpu_limit=1, cpu_request=1, extra_container_config={ "imagePullPolicy": "Always" })
scheduler_template = make_pod_spec(image='holdenk/dask:latest',
                         memory_limit='4G', memory_request='4G',
                         cpu_limit=1, cpu_request=1, extra_container_config={ "imagePullPolicy": "Always" })
cluster = KubeCluster(pod_template = worker_template, scheduler_pod_template = scheduler_template)
cluster.adapt(minimum=1)    # or create and destroy workers dynamically based on workload
from dask.distributed import Client
client = Client(cluster)
#end::make_dask_k8s_client[]


# In[ ]:


client


# In[ ]:


client.dashboard_link


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
local_memoized_time = timeit.timeit(lambda: fib(14), number=1)
print("In sequence {}, in parallel {}, local memoized {}".format(seq_time, dask_time, local_memoized_time))
#end::fib_task_hello_world[]


# In[ ]:


#tag::fail_to_ser[]
class ConnectionClass:
    def __init__(self, host, port):
        import socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

@dask.delayed
def bad_fun(x):
    return ConnectionClass("www.scalingpythonml.com", 80)

# Fails to serialize
if False:
    dask.compute(bad_fun(1))
#end::fail_to_ser[]


# In[ ]:


#tag::custom_serializer_not_own_class[]

class SerConnectionClass:
    def __init__(self, conn):
        import socket
        self.conn = conn

    def __getstate__(self):
        state_dict = {"host": self.conn.socket.getpeername()[0], "port": self.conn.socket.getpeername()[1]}
        return state_dict

    def __setsate__(self, state):
        self.conn = ConnectionClass(state["host"], state["port"])
#end::custom_serializer_not_own_class[]


# In[ ]:


# now we can sort of serialize the connection
@dask.delayed
def ok_fun(x):
    return SerConnectionClass(ConnectionClass("www.scalingpythonml.com", 80))

dask.compute(ok_fun(1))


# In[ ]:


# See https://github.com/dask/distributed/issues/5561
@dask.delayed
def bad_fun(x):
    return ConnectionClass("www.scalingpythonml.com", 80)

from distributed.protocol import dask_serialize, dask_deserialize

@dask_serialize.register(ConnectionClass)
def serialize(bad: ConnectionClass) -> Tuple[Dict, List[bytes]]:
    import cloudpickle
    header = {}
    frames = [cloudpickle.dumps({"host": bad.socket.getpeername()[0], "port": bad.socket.getpeername()[1]})]
    return header, frames

@dask_deserialize.register(ConnectionClass)
def deserialize(bad: Dict, frames: List[bytes]) -> ConnectionClass:
    import cloudpickle
    info = cloudpickle.loads(frames[0])
    return ConnectionClass(info["host"], info["port"])

# note: this does not work because dask_serialize didn't make it to the worker :/
# dask.compute(bad_fun(1))


# In[ ]:


#tag::serialize_class_with_numpy[]
class NumpyInfo:
    def __init__(self, name: str, features: npt.ArrayLike):
        self.name = name
        self.features = features
        
i = NumpyInfo("boo", np.array(0))
numpybits = [i]

# Surprisingly this works, despite the implication that we would need to call register_generic
from distributed.protocol import register_generic
register_generic(NumpyInfo)

dask.compute(ok_fun(1))
#end::serialize_class_with_numpy[]


# In[ ]:


dask.visualize(ok_fun(1))


# In[ ]:


ok_fun(1).visualize()


# In[ ]:


ok_fun(1)


# In[ ]:


# From ch2 for visualize
@dask.delayed
def crawl(url, depth=0, maxdepth=1, maxlinks=4):
    links = []
    link_futures = []
    try:
        import requests
        from bs4 import BeautifulSoup
        f = requests.get(url)
        links += [(url, f.text)]
        if (depth > maxdepth):
            return links # base case
        soup = BeautifulSoup(f.text, 'html.parser')
        c = 0
        for link in soup.find_all('a'):
            if "href" in link:
                c = c + 1
                link_futures += crawl(link["href"], depth=(depth+1), maxdepth=maxdepth)
                # Don't branch too much were still in local mode and the web is big
                if c > maxlinks:
                    break
        for r in dask.compute(link_futures):
            links += r
        return links
    except requests.exceptions.InvalidSchema:
        return [] # Skip non-web links
import dask.bag as db
githubs = ["https://github.com/scalingpythonml/scalingpythonml", "https://github.com/dask/distributed"]
initial_bag = db.from_delayed(map(crawl, githubs))
words_bag = initial_bag.map(lambda url_contents: url_contents[1].split(" ")).flatten()
#tag::visualize[]
dask.visualize(words_bag.frequencies())
#end::visualize[]


# In[ ]:


dask.visualize(words_bag.frequencies(), filename="wc.pdf")


# In[ ]:


dir(cluster)


# In[ ]:



import dask.array as da
#tag::make_chunked_array[]
distributed_array = da.from_array(list(range(0, 10000)), chunks=10)
#end::make_chunked_array[]


# In[ ]:


# From ch2 so we can continue the WC example
@dask.delayed
def crawl(url, depth=0, maxdepth=1, maxlinks=4):
    links = []
    link_futures = []
    try:
        import requests
        from bs4 import BeautifulSoup
        f = requests.get(url)
        links += [(url, f.text)]
        if (depth > maxdepth):
            return links # base case
        soup = BeautifulSoup(f.text, 'html.parser')
        c = 0
        for link in soup.find_all('a'):
            if "href" in link:
                c = c + 1
                link_futures += crawl(link["href"], depth=(depth+1), maxdepth=maxdepth)
                # Don't branch too much were still in local mode and the web is big
                if c > maxlinks:
                    break
        for r in dask.compute(link_futures):
            links += r
        return links
    except requests.exceptions.InvalidSchema:
        return [] # Skip non-web links


# In[ ]:


import dask.bag as db
githubs = ["https://github.com/scalingpythonml/scalingpythonml", "https://github.com/dask/distributed"]
some_bag = db.from_delayed(map(crawl, githubs))
#tag::repartition_bag[]
some_bag.repartition(npartitions=10)
#end::repartition_bag[]


# In[ ]:


some_bag.npartitions


# In[ ]:


distributed_array.chunks


# In[ ]:


import dask.dataframe as dd
df = dd.from_dask_array(distributed_array)


# In[ ]:


df.index


# In[ ]:


#tag::manual_persist[]
df.persist
# You do a bunch of things on DF

# I'm done!
from distributed.client import futures_of
list(map(lambda x: x.release(), futures_of(df)))
#end::manual_persist[]


# In[ ]:





# In[ ]:




