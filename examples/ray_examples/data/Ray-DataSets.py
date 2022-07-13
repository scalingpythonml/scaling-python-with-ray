#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ray
from typing import *
import dask
import pyspark


# In[ ]:


local=True


# In[ ]:


if local:
    ray.init(num_cpus=30)
else:
    # Connect to the ray cluster
    CLUSTER_NAME = "gpu-cluster"
    NAMESPACE = "ray"
    PORT=10001
    # The dns name is based off of the service name which is [cluster]-ray-head & namespace
    dns_name = f"{CLUSTER_NAME}-ray-head.{NAMESPACE}.svc"
    ray.util.connect(f"{dns_name}:{PORT}")


# In[ ]:


import ray.data


# In[ ]:


trivial_ds = ray.data.from_items([
    "https://github.com/scalingpythonml/scalingpythonml",
    "https://github.com/ray-project/ray"])
ray.get(trivial_ds.get_internal_block_refs())


# In[ ]:


get_ipython().system('wget http://gender-pay-gap.service.gov.uk/viewing/download-data/2021')


# In[ ]:


# If in local mode
if local:
    #tag::load_csv_local_fs[]
    ds = ray.data.read_csv("2021")
    #end::load_csv_local_fs[]


# In[ ]:


import fsspec


# In[ ]:


from fsspec.registry import known_implementations


# In[ ]:


fsspec.filesystem('http')


# In[ ]:


known_implementations


# In[ ]:


try:
    fsspec.filesystem('gcs')
except Exception as e:
    print(e)


# In[ ]:


#tag::load_from_https[]
fs = fsspec.filesystem('https')
ds = ray.data.read_csv(
    "https://https://gender-pay-gap.service.gov.uk/viewing/download-data/2021",
    filesystem=fs)
#end::load_from_https[]


# In[ ]:


ray.get(ds.get_internal_block_refs())


# In[ ]:


from ray.util import inspect_serializability
inspect_serializability(fs)


# In[ ]:


inspect_serializability(ray.get(ds.get_internal_block_refs()))


# In[ ]:


#tag::batch_op_on_pandas[]
# Kind of hacky string munging to get a median-ish to weight our values.
def update_empsize_to_median(df):
    def to_median(value):
        if " to " in value:
            f , t = value.replace(",", "").split(" to ")
            return (int(f) + int(t)) / 2.0
        elif "Less than" in value:
            return 100
        else:
            return 10000
    df["EmployerSize"] = df["EmployerSize"].apply(to_median)
    return df

ds_with_median = ds.map_batches(update_empsize_to_median, batch_format="pandas")
#end::batch_op_on_pandas[]


# In[ ]:


#tag::agg[]
def init_func(key):
    # First elem is weighted total, second is weights
    return [0, 0]

def accumulate_func(accumulated, row):
    return [
        accumulated[0] + (float(row["EmployerSize"]) * float(row["DiffMeanHourlyPercent"])),
        accumulated[1] + row["DiffMeanHourlyPercent"]]
        
def combine_aggs(agg1, agg2):
    return (agg1[0] + agg2[0], agg1[1] + agg2[1])

def finalize(agg):
    if agg[1] != 0:
        return agg[0] / agg[1]
    else:
        return 0
    
weighted_mean = ray.data.aggregate.AggregateFn(
    name='weighted_mean',
    init=init_func,
    merge=combine_aggs,
    accumulate=accumulate_func,
    finalize=finalize)
aggregated = ds_with_median.groupby("PostCode").aggregate(weighted_mean)
#end::agg[]


# In[ ]:


aggregated.to_pandas()


# In[ ]:


#tag::batch_op_on_pandas_from_raw[]
def sup(df):
    return list(str(df.info()))

trivial_ds.map_batches(sup, batch_format="pandas")
#end::batch_op_on_pandas_from_raw[]


# In[ ]:


ds_with_median.show()


# In[ ]:


#tag::to_dask[]
dask_df = ds.to_dask()
#end::to_dask[]


# In[ ]:


#tag::to_spark[]
spark_df = ds.to_spark()
#end::to_spark[]


# In[ ]:


#tag::ds[]
# Create a Dataset of URLS objects. We could also load this from a text file with ray.data.read_text()
urls = ray.data.from_items([
    "https://github.com/scalingpythonml/scalingpythonml",
    "https://github.com/ray-project/ray"])

def fetch_page(url):
    import requests
    f = requests.get(url)
    return f.text

pages = urls.map(fetch_page)
# Look at a page to make sure it worked
pages.take(1)
#end::ds[]
#tag::ray_wordcount_on_ds_filter_only_once[]
words = pages.flat_map(lambda x: x.split(" ")).map(lambda w: (w, 1))
grouped_words = words.groupby(lambda wc: wc[0])
interesting_words = groupd_words.filter(lambda wc: wc[1] > 1)
#end::ray_wordcount_on_ds_filter_only_once[]
interesting_words.show()


# In[ ]:


#tag::ray_wordcount_on_ds_filter_only_once_with_batches[]
def tokenize_batch(batch):
    nested_tokens = map(lambda s: s.split(" "), batch)
    # Flatten the result
    nr = []
    for r in nested_tokens:
        nr.extend(r)
    return nr

def pair_batch(batch):
    return list(map(lambda w: (w, 1), batch))

def filter_for_interesting(batch):
    return list(filter(lambda wc: wc[1] > 1, batch))

words = pages.map_batches(tokenize_batch).map_batches(pair_batch)
# The one part we can't rewrite with map_batches since it involves a shuffle
grouped_words = words.groupby(lambda wc: wc[0]) 
interesting_words = groupd_words.map_batches(filter_for_interesting)
#end::ray_wordcount_on_ds_filter_only_once_with_batches[]
interesting_words.show()


# In[ ]:


# Note to holden - move this to the dataset chapter for showing how to integrate with remote functions
# and talk about why.
#tag::more_awesome_wordcount[]
runtime_env = {"pip": ["bs4"]}
parse_env = {"pip": ["bs4", "nltk"]}

# Note - not remote
def fetch(url: str) -> Tuple[str, str]:
    import urllib.request
    with urllib.request.urlopen(url) as response:
       return (url, response.read())

# This is remote because we want to use bs4
@ray.remote(runtime_env=runtime_env)
def extract_text(url_text: Tuple[str, str]) -> str:
    from bs4 import BeautifulSoup
    html = url_text[1]
    return str(BeautifulSoup(html, 'html.parser').text)

# This is remote because we want to use nltk
@ray.remote(runtime_env=parse_env)
def tokenize(text: str):
    import nltk
    nltk.download('punkt')
    from nltk.tokenize import word_tokenize
    return list(word_tokenize(text))

urls = ray.data.from_items(["http://www.holdenkarau.com", "http://www.google.com"])

pages = urls.map(fetch)
# This 
page_text = pages.map(lambda r: ray.get(extract_text.remote(r)))
words = page_text.flat_map(lambda r: ray.get(tokenize.remote(r)))
word_count = words.groupby(lambda x: x).count()
word_count.show()
#end::more_awesome_wordcount[]


# In[ ]:


#tag::more_awesome_wordcount_with_batches[]
def extract_text_for_batch(sites):
    text_futures = map(lambda s: extract_text.remote(s), sites)
    result = ray.get(list(text_futures))
    # ray.get returns None on an empty input, but map_batches requires lists
    if result is None:
        return []
    return result

def tokenize_batch(texts):
    token_futures = map(lambda s: tokenize.remote(s), texts)
    result = ray.get(list(token_futures))
    if result is None:
        return []
    # Flatten the result
    nr = []
    for r in result:
        nr.extend(r)
    return nr


# Exercise to the reader: generalize the above patterns - note the flatten magic difference

urls = ray.data.from_items(["http://www.holdenkarau.com", "http://www.google.com"])

pages = urls.map(fetch)

page_text = pages.map_batches(extract_text_for_batch)
words = page_text.map_batches(tokenize_batch)
word_count = words.groupby(lambda x: x).count()
word_count.show()
#end::more_awesome_wordcount_with_batches[]


# In[ ]:




