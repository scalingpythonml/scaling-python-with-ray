#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ray
from typing import *


# In[ ]:


ray.init(num_cpus=20)


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


#tag::even_more_awesome_wordcount[]
def extract_text_for_batch(sites):
    text_futures = map(lambda s: extract_text.remote(s), sites)
    result = ray.get(list(text_futures))
    # ray.get returns None on an empty input, but map_batches requires lists
    if result is None:
        return []
    return result

def tokenize_batch(texts):
    token_futures = map(lambda s: extract_text.remote(s), texts)
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
# This 
page_text = pages.map_batches(extract_text_for_batch)
words = page_text.map_batches(tokenize_batch)
word_count = words.groupby(lambda x: x).count()
word_count.show()
#tag::even_more_awesome_wordcount[]


# In[ ]:




