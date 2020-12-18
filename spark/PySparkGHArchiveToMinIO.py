#!/usr/bin/env python
# coding: utf-8

# In[1]:


#tag::sparkImports[]
from pyspark import *
from pyspark.context import *
from pyspark.conf import *
#end::sparkImports[]


# In[2]:


#tag::makeSparkConf[]
conf = (SparkConf().setMaster("k8s://https://kubernetes.default")
#end::markMakeSparkConf[]
    .set("spark.executor.instances", "2")
#tag::configureContainer[]
    .set("spark.kubernetes.container.image", "holdenk/spark-py:v3.0.1.2")
#end::configureContainer[]
#tag::configureService[]
    .set("spark.driver.port", "2222") # Needs to match svc
    .set("spark.driver.blockManager.port", "7777")
    .set("spark.driver.host", "driver-service.jhub.svc.cluster.local") # Needs to match svc
    .set("spark.driver.bindAddress", "0.0.0.0") #  Otherwise tries to bind to svc IP, will fail
#end::configureService[]
    .set("spark.kubernetes.namespace", "spark")
    .set("spark.app.name", "PySparkHelloWorldInsideTheCluster")
    )


# In[3]:


#tag::makeSparkWithConf[]
sc = SparkContext(conf=conf)
#end::makeSparkWithConf[]


# In[4]:


rdd = sc.parallelize(range(100))


# In[5]:


rdd.sum()


# In[6]:


import datetime


# In[7]:


current_date=datetime.datetime(2020,10,1, 1)
gh_archive_files = []
while current_date < datetime.datetime.now() -  datetime.timedelta(days=1):
    current_date = current_date + datetime.timedelta(hours=1)
    datestring = f'{current_date.year}-{current_date.month:02}-{current_date.day:02}-{current_date.hour}'
    gh_url = f'http://data.githubarchive.org/{datestring}.json.gz'
    gh_archive_files.append(gh_url)


# In[8]:


#tag::sparkSQLImports[]
from pyspark.sql import *
#end::sparkSQLImports[]


# In[ ]:


#tag::makeSession[]
# Make a session using the existing SparkContext or default config
session = SparkSession.builder.getOrCreate()
#end::makeSession[]


# In[ ]:


session


# In[ ]:


#tag::fetchGzippedURL[]
def fetch_gzipped_file(url):
    """Fetch a gzipped file"""
    import tempfile
    import urllib.request
    
    tf = tempfile.NamedTemporaryFile()

    # The default urlretrive user agent seems to be on the do not allow list
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, tf.name)
    
    # Load data and decompress, I _think_ this streams data
    import gzip
    fh = gzip.open(tf.name, 'r')
    while True:
        line = fh.readline()
        if not line:
            break
        yield line
#end::fetchGzippedURL[]


# In[ ]:


# Quick verification
r = fetch_gzipped_file('https://data.githubarchive.org/2020-10-01-2.json.gz')
list(r)


# In[ ]:


gh_archive_files[0]


# In[ ]:


get_ipython().system('wget https://data.githubarchive.org/2020-10-01-2.json.gz')


# In[ ]:


#tag::loadData[]
# Unlike in Dask we can't directly load from HTTP so we'll do some magic
rdd_of_urls = sc.parallelize([gh_archive_files[0]])


# In[ ]:


rdd_of_records = rdd_of_urls.flatMap(fetch_gzipped_file)


# In[ ]:


rdd_of_records.cache()


# In[ ]:


rdd_of_records.take(2)


# In[ ]:


df = session.read.json(rdd_of_records)


# In[ ]:


#end::loadData[]


# In[ ]:


df.cache()


# In[ ]:


df.take(1)


# In[ ]:




