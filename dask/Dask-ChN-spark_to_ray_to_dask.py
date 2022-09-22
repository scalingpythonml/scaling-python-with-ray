#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import sys

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


# In[4]:


from pyspark.sql.session import SparkSession
from pyspark.sql import SQLContext



# In[5]:


get_ipython().system('java -version')


# In[6]:


import pyspark

# number_cores = 1
# memory_gb = 8
# conf = (
#     pyspark.SparkConf()
# #         .master('spark://xxx.xxx.xx.xx:7077') \
#         .setMaster('local[{}]'.format(number_cores)) \
#         .set('spark.driver.memory', '{}g'.format(memory_gb))        
# )
# sc = pyspark.SparkContext(conf=conf)
# # sqlContext = SQLContext(sc)
# sqlContext = SQLContext(sc)
# #http://localhost:4040/jobs/


# In[ ]:





# In[7]:


import raydp
import ray 

ray.init()
spark = raydp.init_spark(
  app_name = "raydp_spark",
  num_executors = 1,
  executor_cores = 1,
  executor_memory = "4GB"
)


# In[86]:


from ray.util.dask import ray_dask_get, enable_dask_on_ray, disable_dask_on_ray

enable_dask_on_ray()


# In[ ]:





# In[ ]:


df = spark.createDataFrame(["Anna","Bob","Sue"], "string").toDF("firstname")


# In[9]:


df.show()


# In[10]:


names = ["Anna", "Bob", "Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Elijah", "Charlotte"]
class StudentRecord:
    def __init__(self, record_id, name):
        self.record_id = record_id
        self.name = name
    def __str__(self):
        return f'StudentRecord(record_id={self.record_id},data={self.name})'
    
num_records = len(names)
student_records = [StudentRecord(i, f'{names[i]}') for i in range(num_records)] 


# In[11]:


student_records


# In[12]:


df = spark.createDataFrame(student_records, ['name', 'id'])


# In[13]:


df.show()


# In[ ]:





# In[ ]:





# In[14]:


ray_dataset = ray.data.from_spark(df)


# In[15]:


ray_dataset.show()


# In[16]:


from ray.util.dask import ray_dask_get, enable_dask_on_ray, disable_dask_on_ray
import dask.array as da
import dask.dataframe as dd
import numpy as np
import pandas as pd


# In[ ]:





# In[22]:


import dask


# In[ ]:


# ray.data.dataset.Dataset.to_dask


# In[23]:


ddf_students = ray.data.dataset.Dataset.to_dask(ray_dataset) 


# In[26]:


ddf_students.head()


# In[60]:


from ray.util.dask import ray_dask_get


# In[87]:


dask.config.get


# In[88]:


dsk_config_dump = dask.config.config.get('distributed')


# In[91]:


dsk_config_dump.get('dashboard').get('link')


# In[ ]:





# In[ ]:





# In[ ]:


# cluster.scheduler.services['dashboard'].server.address


# In[ ]:





# In[ ]:


# larger dataset


# In[34]:


url = "https://gender-pay-gap.service.gov.uk/viewing/download-data/2021"
from pyspark import SparkFiles


# In[35]:


spark.sparkContext.addFile(url)


# In[36]:





# In[40]:


df = spark.read.csv("file://"+SparkFiles.get("2021"), header=True, inferSchema= True)


# In[47]:


df.show(3)


# In[42]:


ray_dataset = ray.data.from_spark(df)


# In[46]:


ray_dataset.show(3)


# In[49]:


from dask.distributed import Client
client = Client()


# In[ ]:





# In[51]:


ddf_pay = ray.data.dataset.Dataset.to_dask(ray_dataset) 


# In[52]:


ddf_pay.compute()


# In[45]:


ddf_pay.head(3)


# In[50]:





# In[54]:


def fillna(df):
    return df.fillna(value={"PostCode": "UNKNOWN"}).fillna(value=0)
    
new_df = ddf_pay.map_partitions(fillna)


# In[55]:


new_df.compute()


# In[56]:


# Since there could be an NA in the index clear the partition / division information
new_df.clear_divisions()
new_df.compute()
narrow_df = new_df[["PostCode", "EmployerSize", "DiffMeanHourlyPercent"]]


# In[57]:


grouped_df = narrow_df.groupby("PostCode")


# In[59]:


avg_by_postalcode = grouped_df.mean()


avg_by_postalcode.compute()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


sc.stop()


# In[ ]:


sqlContext.stop()

