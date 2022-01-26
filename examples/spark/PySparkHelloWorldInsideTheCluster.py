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
#end::makeSparkConf[]
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
#tag::configureNamespace[]
    .set("spark.kubernetes.namespace", "spark")
#end::configureNamespace[]
#tag::configureSparkAppName[]
    .set("spark.app.name", "PySparkHelloWorldInsideTheCluster")
#end::configureSparkAppName[]
    )


# In[3]:


#tag::makeSparkWithConf[]
sc = SparkContext(conf=conf)
#end::makeSparkWithConf[]


# In[4]:


rdd = sc.parallelize(range(100))


# In[5]:


rdd.sum()


# In[ ]:




