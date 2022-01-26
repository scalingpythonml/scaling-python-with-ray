#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Make sure were on ray 1.9
from ray.data.grouped_dataset import GroupedDataset


# In[ ]:


#tag::start-ray-local[]
import ray
ray.init(num_cpus=20) # In theory auto sensed, in practice... eh
#end::start-ray-local[]


# In[ ]:


#tag::local_fun[]
def hi():
    import os
    import socket
    return f"Running on {socket.gethostname()} in pid {os.getpid()}"
#end::local_fun[]


# In[ ]:


hi()


# In[ ]:


#tag::remote_fun[]
@ray.remote
def remote_hi():
    import os
    import socket
    return f"Running on {socket.gethostname()} in pid {os.getpid()}"
future = remote_hi.remote()
ray.get(future)
#end::remote_fun[]


# In[ ]:


#tag::sleepy_task_hello_world[]
import timeit

def slow_task(x):
    import time
    time.sleep(2) # Do something sciency/business
    return x

@ray.remote
def remote_task(x):
    return slow_task(x)

things = range(10)

very_slow_result = map(slow_task, things)
slowish_result = map(lambda x: remote_task.remote(x), things)

slow_time = timeit.timeit(lambda: list(very_slow_result), number=1)
fast_time = timeit.timeit(lambda: list(ray.get(list(slowish_result))), number=1)
print(f"In sequence {slow_time}, in parallel {fast_time}")
#end::sleepy_task_hello_world[]


# In[ ]:


slowish_result = map(lambda x: remote_task.remote(x), things)
ray.get(list(slowish_result))


# In[ ]:


# Note: if we were on a "real" cluster we'd have to do more magic to install it on all the nodes in the cluster.
get_ipython().system('pip install bs4')


# In[ ]:


#tag::mini_crawl_task[]
@ray.remote
def crawl(url, depth=0, maxdepth=1, maxlinks=4):
    links = []
    link_futures = []
    import requests
    from bs4 import BeautifulSoup
    try:
        f = requests.get(url)
        links += [(url, f.text)]
        if (depth > maxdepth):
            return links # base case
        soup = BeautifulSoup(f.text, 'html.parser')
        c = 0
        for link in soup.find_all('a'):
            try:
                c = c + 1
                link_futures += [crawl.remote(link["href"], depth=(depth+1), maxdepth=maxdepth)]
                # Don't branch too much were still in local mode and the web is big
                if c > maxlinks:
                    break
            except:
                pass
        for r in ray.get(link_futures):
            links += r
        return links
    except requests.exceptions.InvalidSchema:
        return [] # Skip non-web links
    except requests.exceptions.MissingSchema:
        return [] # Skip non-web links

ray.get(crawl.remote("http://holdenkarau.com/"))
#end::mini_crawl_task[]


# In[ ]:


#tag::actor[]
@ray.remote
class HelloWorld(object):
    def __init__(self):
        self.value = 0
    def greet(self):
        self.value += 1
        return f"Hi user #{self.value}"

hello_actor = HelloWorld.remote()


# In[ ]:


print(ray.get(hello_actor.greet.remote()))
print(ray.get(hello_actor.greet.remote()))
#end::actor[]


# In[ ]:


#tag::ds[]
# Create a Dataset of URLS objects. We could also load this from a text file with ray.data.read_text()
urls = ray.data.from_items([
    "https://github.com/scalingpythonml/scalingpythonml",
    "https://github.com/ray-project/ray"])


# In[ ]:


def fetch_page(url):
    import requests
    f = requests.get(url)
    return f.text


# In[ ]:


pages = urls.map(fetch_page)


# In[ ]:


pages.take(1)


# In[ ]:


#end:ds[]


# In[ ]:


#tag::ray_wordcount_on_ds[]
words = pages.flat_map(lambda x: x.split(" ")).map(lambda w: (w, 1))


# In[ ]:


grouped_words = words.groupby(lambda wc: wc[0])
#end::ray_wordcount_on_ds[]


# In[ ]:


word_counts = grouped_words.count()


# In[ ]:


word_counts.show()


# In[ ]:




