#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#tag::make_dask_client[]
import dask
from dask.distributed import Client
client = Client() # Here we could specify a cluster, defaults to local mode
#end::make_dask_client[]


# In[ ]:


#tag::sleepy_task_hello_world[]
import timeit

def slow_task(x):
    import time
    time.sleep(2) # Do something sciency/business
    return x

things = range(10)

very_slow_result = map(slow_task, things)
slowish_result = map(dask.delayed(slow_task), things)

slow_time = timeit.timeit(lambda: list(very_slow_result), number=1)
fast_time = timeit.timeit(lambda: list(dask.compute(*slowish_result)), number=1)
print("In sequence {}, in parallel {}".format(slow_time, fast_time))
#end::sleepy_task_hello_world[]


# In[ ]:


d = dask.delayed(slow_task)(1)
d


# In[ ]:


f = client.submit(d)
f


# In[ ]:


# Note: if we were on a cluster we'd have to do more magislowish_result = map(dask.delayed(slow_task), things)c to install it on all the nodes in the cluster.
get_ipython().system('pip install bs4')


# In[ ]:


#tag::mini_crawl_task[]
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

dask.compute(crawl("http://holdenkarau.com/"))
#end::mini_crawl_task[]


# In[ ]:


#tag::make_bag_of_crawler[]
import dask.bag as db
githubs = ["https://github.com/scalingpythonml/scalingpythonml", "https://github.com/dask/distributed"]
initial_bag = db.from_delayed(map(crawl, githubs))
#end::make_bag_of_crawler[]


# In[ ]:


#tag::make_a_bag_of_words[]
words_bag = initial_bag.map(lambda url_contents: url_contents[1].split(" ")).flatten()
#end::make_a_bag_of_words[]


# In[ ]:


#tag::wc_freq[]
dask.compute(words_bag.frequencies())
#end::wc_freq[]


# In[ ]:


#tag::wc_func[]
def make_word_tuple(w):
    return (w, 1)

def get_word(word_count):
    return word_count[0]

def sum_word_counts(wc1, wc2):
    return (wc1[0], wc1[1] + wc2[1])

word_count = words_bag.map(make_word_tuple).foldby(get_word, sum_word_counts)
#end::wc_func[]


# In[ ]:


dask.compute(word_count)


# In[ ]:


#tag::wc_dataframe
import dask.dataframe as dd

@dask.delayed
def crawl_to_df(url, depth=0, maxdepth=1, maxlinks=4):
    import pandas as pd
    crawled = crawl(url, depth=depth, maxdepth=maxdepth, maxlinks=maxlinks)
    return pd.DataFrame(crawled.compute(), columns=["url", "text"]).set_index("url")

delayed_dfs = map(crawl_to_df, githubs)
initial_df = dd.from_delayed(delayed_dfs)
wc_df = initial_df.text.str.split().explode().value_counts()

dask.compute(wc_df)
#end::wc_dataframe


# In[ ]:


#tag::dask_array[]
import dask.array as da
distributed_array = da.from_array(list(range(0, 1000)))
avg = dask.compute(da.average(distributed_array))
#end::dask_array[]
avg


# In[ ]:


na = distributed_array.persist()
na


# In[ ]:


dir(na)


# In[ ]:


na = None


# In[ ]:


#tag::cache[]
from dask.cache import Cache

c = Cache(1e9) # 1GB cache
# A local cache for the part of our code where we need a cache
with c:
    distributed_array.compute()
    
# Or global for any calls we make
c.register()
#end::cache[]


# In[ ]:





# In[ ]:




