#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ray
from typing import *


# In[ ]:


ray.init(num_cpus=20)


# In[ ]:


import ray.data


# In[ ]:


get_ipython().system('wget http://gender-pay-gap.service.gov.uk/viewing/download-data/2021')


# In[ ]:


get_ipython().system('pip install fsspec aiohttp')


# In[ ]:


#tag::load_csv_local_fs[]
ds = ray.data.read_csv("2021")
#end::looad_csv_local_fs[]


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
ds = ray.data.read_csv(
    "https://https://gender-pay-gap.service.gov.uk/viewing/download-data/2021",
    filesystem=fsspec.filesystem('https'))
#end::load_from_https[]


# In[ ]:




