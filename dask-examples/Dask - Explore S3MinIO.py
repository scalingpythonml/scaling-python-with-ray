#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dask
from dask_kubernetes import KubeCluster
import numpy as np
import pyarrow


# In[2]:


# Specify a remote deployment using a load blanacer if we are running the NB outside of the cluster
#dask.config.set({"kubernetes.scheduler-service-type": "LoadBalancer"})


# In[3]:


cluster = KubeCluster.from_yaml('worker-spec.yaml', namespace='dask') # deploy_mode='remote')


# In[4]:


cluster.adapt(minimum=1, maximum=10)


# In[5]:


# Example usage
from dask.distributed import Client
import dask.array as da

# Connect Dask to the cluster
client = Client(cluster)
client # the repr gives us useful links


# In[6]:


client.scheduler_comm.comm.handshake_info()


# In[7]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# So now we know the cluster is doing ok :)

# Configure dask to talk to our local MinIO

# In[8]:


# The anon false wasted so much time
minio_storage_options = {
#    "anon": "false",
    "key": "YOURACCESSKEY",
    "secret": "YOURSECRETKEY",
    "client_kwargs": {
        "endpoint_url": "http://minio-1602984784.minio.svc.cluster.local:9000",
        "region_name": 'us-east-1'
    },
    "config_kwargs": {"s3": {"signature_version": 's3v4'}},
}

#tag::minio_storage_options[]
minio_storage_options = {
    "key": "YOURACCESSKEY",
    "secret": "YOURSECRETKEY",
    "client_kwargs": {
        "endpoint_url": "http://minio-1602984784.minio.svc.cluster.local:9000",
        "region_name": 'us-east-1'
    },
    "config_kwargs": {"s3": {"signature_version": 's3v4'}},
}
#end::minio_storage_options[]


# Download the GH archive data

# In[9]:


import datetime
import dask.dataframe as dd


# In[10]:


current_date=datetime.datetime(2020,10,1, 1)


# In[11]:





# In[12]:


#tag::make_file_list[]
gh_archive_files=[]
while current_date < datetime.datetime.now() -  datetime.timedelta(days=1):
    current_date = current_date + datetime.timedelta(hours=1)
    datestring = f'{current_date.year}-{current_date.month:02}-{current_date.day:02}-{current_date.hour}'
    gh_url = f'http://data.githubarchive.org/{datestring}.json.gz'
    gh_archive_files.append(gh_url)
#end::make_file_list[]


# In[13]:


gh_archive_files[0]


# In[14]:


#tag::load_data[]
df = dd.read_json(gh_archive_files, compression='gzip')
df.columns
#end::load_data[]


# In[15]:


len(df)


# In[16]:


# What kind of file systems are supported?
#tag::known_fs[]
from fsspec.registry import known_implementations
known_implementations
#end::known_fs[]
#tag::known_fs_result[]


# In[ ]:


#end::known_fs_result[]


# What does our data look like?

# In[17]:


df.columns


# In[18]:


h = df.head()
h


# In[19]:


import pandas as pd
j = pd.io.json.json_normalize(h.repo)
j


# In[20]:


j.name


# Since we want to partition on the repo name, we need to extract that to it's own column

# In[21]:


data_bag = df.to_bag()


# In[22]:


# The records returned by the bag are tuples not named tuples, so use the df columns to look up the tuple index
cols = df.columns


# In[23]:


def parse_record(record):
    r = {
        "repo": pd.io.json.json_normalize(record[cols.get_loc("repo")]),
        "repo_name": record[cols.get_loc("repo")]["name"],
        "type": record[cols.get_loc("type")],
        "id": record[cols.get_loc("id")],
        "created_at": record[cols.get_loc("created_at")],
        "payload": pd.io.json.json_normalize(record[cols.get_loc("payload")])}
    return r

#tag::cleanup[]
def clean_record(record):
    r = {
        "repo": record[cols.get_loc("repo")],
        "repo_name": record[cols.get_loc("repo")]["name"],
        "type": record[cols.get_loc("type")],
        "id": record[cols.get_loc("id")],
        "created_at": record[cols.get_loc("created_at")],
        "payload": record[cols.get_loc("payload")]}
    return r

cleaned_up_bag = data_bag.map(clean_record)
res = cleaned_up_bag.to_dataframe()
#end::cleanup[]
parsed_bag = data_bag.map(parse_record)


# In[24]:


cleaned_up_bag.take(1)


# In[25]:


res = cleaned_up_bag.to_dataframe()
parsed_res = parsed_bag.to_dataframe()
h = res.head()
h_parsed = parsed_res.head()


# In[26]:


h


# In[27]:


type(h.iloc[0]["repo"])


# In[28]:


type(h_parsed.iloc[0]["repo"])


# In[29]:


#to_csv brings it back locally, lets try parquet. csv doesn't handle nesting so well so use original json inside
df.to_csv("s3://dask-test/boop-test-csv", storage_options=minio_storage_options)


# In[30]:


# This will probably still bring everything back to the client? I'm guessing though.
res.to_parquet("s3://dask-test/boop-test-pq", compression="gzip", storage_options=minio_storage_options, engine="pyarrow")


# In[31]:


parsed_res.to_parquet("s3://dask-test/boop-test-pq-p-nested", compression="gzip", storage_options=minio_storage_options, engine="fastparquet")


# In[ ]:


#tag::write[]
res.to_parquet("s3://dask-test/boop-test-partioned",
              partition_on=["type", "repo_name"], # Based on " there will be no global groupby." I think this is the value we want.
              compression="gzip",
              storage_options=minio_storage_options, engine="pyarrow")
#end::write[]


# In[ ]:




