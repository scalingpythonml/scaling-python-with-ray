#!/usr/bin/env python
# coding: utf-8

# In[6]:


# !pip install scikeras>=0.1.8
# !pip install tensorflow>=2.3.0
# !pip install -U skorch
# !pip install torch
# !pip install torchvision
# !pip install pytorch-cpu #not sure if i need to fix this
# !pip install s3fs
# !pip install dask_kubernetes
# !pip install pyarrow
# !pip install xgboost


# In[34]:


# !pip install cloudpickle==2.1.0
# !pip install dask==2022.05.0
# !pip install distributed==2022.5.0
# !pip install lz4==4.0.0
# !pip install msgpack==1.0.3
# !pip install toolz==0.11.2
# !pip install xgboost


# In[ ]:





# In[ ]:





# In[4]:





# In[1]:


# https://coiled.io/blog/tackling-unmanaged-memory-with-dask/
# filename = 'https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2013-01.parquet'


# In[1]:


from dask.distributed import Client
# when working with clusters, specify cluster config, n_workers and worker_size
client = Client(n_workers=4, 
                       threads_per_worker=1,
                       memory_limit=0)


# In[2]:


import dask.dataframe as dd
import pandas as pd


# In[3]:


client


# In[12]:


#tag::ex_load_nyc_taxi[]
filename = './nyc_taxi/*.parquet'
df_x = dd.read_parquet(
    filename,
    split_row_groups = 2
)
#end::ex_load_nyc_taxi


# In[13]:


df.dtypes


# In[14]:


df.shape


# In[16]:


df


# In[5]:


df.head()


# In[15]:


#tag::ex_describe_percentiles[]
#remember dask ddf is just pandas df
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.5f' % x)
df.describe(percentiles = [.25, .5, .75]).compute()
#end::ex_describe_percentiles


# In[18]:


#tag::ex_plot_distances[]
import matplotlib.pyplot as plt
import seaborn as sns 
import numpy as np

get_ipython().run_line_magic('matplotlib', 'inline')
sns.set(style="white", palette="muted", color_codes=True)
f, axes = plt.subplots(1, 1, figsize=(11, 7), sharex=True)
sns.despine(left=True)
sns.distplot(np.log(df['trip_distance'].values+1), axlabel = 'Log(trip_distance)', label = 'log(trip_distance)', bins = 50, color="r")
plt.setp(axes, yticks=[])
plt.tight_layout()
plt.show()
#end::ex_plot_distances


# In[ ]:





# In[19]:


# Show that each col is a numpy ndarray. Note how array size is NaN until we call compute.
# chunk sizes compte also shows how this is parallelized.
df['trip_distance'].values.compute_chunk_sizes()


# In[ ]:





# In[20]:


# number of rows
numrows = df.shape[0].compute()
# number of columns
numcols = df.shape[1]
print("Number of rows {} number of columns {}".format(numrows, numcols))


# In[21]:


df['trip_duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).map(lambda x: x.total_seconds())


# In[22]:


df['trip_duration'].describe().compute()


# In[23]:


duration_diff = np.abs(df['trip_duration'])


# In[24]:


# clean up data as we see some dirty inputs
df = df[df['trip_duration'] <= 10000]
df = df[df['trip_duration'] >= 30]


# In[10]:


df['trip_duration'].describe().compute()


# In[11]:


# note numpy -> ddf logic is slightly different. eg df[col].values vs df[col]
# visualizing whole dataset is a different fish to fry, we are just showing small ones for now.
plt.hist(df['trip_duration'], bins=100)
plt.xlabel('trip_duration')
plt.ylabel('number of records')
plt.show()


# In[ ]:





# In[25]:


df['log_trip_duration'] = np.log(df['trip_duration'])


# In[ ]:


plt.hist(df['log_trip_duration'], bins=100)
plt.xlabel('log(trip_duration)')
plt.ylabel('number of records')
plt.show()
sns.distplot(df["log_trip_duration"], bins =100)


# In[ ]:





# In[30]:


#tag::ex_dask_random_split[]
train, test, validation = df.random_split([0.8, 0.1, 0.1], random_state=123)
#end::ex_dask_random_split


# 
# #Start the very tedious job of enriching the dataset, pulling features and categories out

# In[35]:


# Chain them using dask, delay materialization...
# create dummy var out of labels.

# We could've read it at categorical when reading the parquet as specified in dtypes.
# Or we  can do it here.
# unlike pandas, must be categorized before calling dummy.
train = train.categorize("VendorID")
train = train.categorize("VendorID")
train = train.categorize("passenger_count")
train = train.categorize("store_and_fwd_flag")

test = test.categorize("VendorID")
test = test.categorize("VendorID")
test = test.categorize("passenger_count")
test = test.categorize("store_and_fwd_flag")


# In[36]:


vendor_train = dd.get_dummies(train, columns=["VendorID"], prefix='vi', prefix_sep='_')
test_train = dd.get_dummies(test, columns=["VendorID"], prefix='vi', prefix_sep='_')


# In[40]:


# Full list of categorical vars

vendor_train = dd.get_dummies(train, columns=["VendorID"], prefix='vi', prefix_sep='_')
vendor_test = dd.get_dummies(test, columns=["VendorID"], prefix='vi', prefix_sep='_')

passenger_count_train = dd.get_dummies(train, columns = ['passenger_count'], prefix='pc', prefix_sep='_')
passenger_count_test =dd.get_dummies(test, columns= ['passenger_count'], prefix='pc', prefix_sep='_')
store_and_fwd_flag_train = dd.get_dummies(train, columns = ['store_and_fwd_flag'], prefix='sf', prefix_sep='_')
store_and_fwd_flag_test = dd.get_dummies(test, columns=['store_and_fwd_flag'], prefix='sf', prefix_sep='_')

# enrich the datetime into month/ hour / day, and turn it into dummy
train['Month'] = train['tpep_pickup_datetime'].dt.month
test['Month'] = test['tpep_pickup_datetime'].dt.month
# harder way to to the same thing.
# test['Month'] = (test['tpep_pickup_datetime']).map(lambda x: x.month)
train['DayofMonth'] = train['tpep_pickup_datetime'].dt.day
test['DayofMonth'] = test['tpep_pickup_datetime'].dt.day


# In[42]:


test.groupby('DayofMonth').count().compute()


# In[47]:


test.head()


# In[53]:


train['Hour'] = train['tpep_pickup_datetime'].dt.hour
test['Hour'] = test['tpep_pickup_datetime'].dt.hour

train['dayofweek'] = train['tpep_pickup_datetime'].dt.dayofweek
test['dayofweek'] = test['tpep_pickup_datetime'].dt.dayofweek

train = train.categorize("Month")
test = test.categorize("Month")

train = train.categorize("DayofMonth")
test = test.categorize("DayofMonth")

train = train.categorize("dayofweek")
test = test.categorize("dayofweek")

month_train = dd.get_dummies(train, columns = ['dayofweek'], prefix='m', prefix_sep='_')
month_test = dd.get_dummies(test, columns=['dayofweek'], prefix='m', prefix_sep='_')

dom_train = dd.get_dummies(train, columns = ['dayofweek'], prefix='dom', prefix_sep='_')
dom_test = dd.get_dummies(test, columns=['dayofweek'], prefix='dom', prefix_sep='_')

hour_train = dd.get_dummies(train, columns = ['dayofweek'], prefix='h', prefix_sep='_')
hour_test = dd.get_dummies(test, columns=['dayofweek'], prefix='h', prefix_sep='_')

dow_train = dd.get_dummies(train, columns = ['dayofweek'], prefix='dow', prefix_sep='_')
dow_test = dd.get_dummies(test, columns=['dayofweek'], prefix='dow', prefix_sep='_')
# vendor_test = dd.get_dummies(test, columns=["VendorID"], prefix='vi', prefix_sep='_')


# In[54]:


# calculate and add average speed col
train['avg_speed_h'] = 1000 * train['trip_distance'] / train['trip_duration']
test['avg_speed_h'] = 1000 * test['trip_distance'] / test['trip_duration']


# In[55]:


fig, ax = plt.subplots(ncols=3, sharey=True)
ax[0].plot(train.groupby('Hour').avg_speed_h.mean().compute(), 'bo-', lw=2, alpha=0.7)
ax[1].plot(train.groupby('dayofweek').avg_speed_h.mean().compute(), 'go-', lw=2, alpha=0.7)
ax[2].plot(train.groupby('Month').avg_speed_h.mean().compute(), 'ro-', lw=2, alpha=0.7)
ax[0].set_xlabel('Hour of Day')
ax[1].set_xlabel('Day of Week')
ax[2].set_xlabel('Month of Year')
ax[0].set_ylabel('Average Speed')
fig.suptitle('Average Traffic Speed by Date-part')
plt.show()


# In[ ]:


train_final = train.drop(['VendorID','passenger_count','store_and_fwd_flag', 'Month','DayofMonth','Hour','dayofweek'], axis = 1)
test_final = test.drop(['VendorID','passenger_count','store_and_fwd_flag','Month','DayofMonth','Hour','dayofweek'], axis = 1)
train_final = train_final.drop(['tpep_dropoff_datetime', 'tpep_pickup_datetime', 'trip_duration', 'avg_speed_h'], axis = 1)
test_final = test_final.drop(['tpep_dropoff_datetime', 'tpep_pickup_datetime', 'trip_duration', 'avg_speed_h'], axis = 1)
X_train = train_final.drop(['log_trip_duration'], axis=1)
Y_train = train_final["log_trip_duration"]
X_test = test_final.drop(['log_trip_duration'], axis=1)
Y_test = test_final["log_trip_duration"]


# #end enrich / category step

# In[2]:





# In[ ]:


# Just like standard xgb Dmatrix, but note that we are explicitly passing in columns since we're dealing with Pandas, and that we need to give the colnames for xgb to know feature names


# In[60]:


#tag::ex_xgb_train_plot_importance[]

import xgboost as xgb
dtrain = xgb.DMatrix(X_train, label=Y_train, feature_names=X_train.columns)
dvalid = xgb.DMatrix(X_test, label=Y_test,  feature_names=X_test.columns)
watchlist = [(dtrain, 'train'), (dvalid, 'valid')]
xgb_pars = {'min_child_weight': 1, 'eta': 0.5, 'colsample_bytree': 0.9, 
            'max_depth': 6,
'subsample': 0.9, 'lambda': 1., 'nthread': -1, 'booster' : 'gbtree', 'silent': 1,
'eval_metric': 'rmse', 'objective': 'reg:linear'}
model = xgb.train(xgb_pars, dtrain, 10, watchlist, early_stopping_rounds=2,
      maximize=False, verbose_eval=1)
print('Modeling RMSLE %.5f' % model.best_score)

xgb.plot_importance(model, max_num_features=28, height=0.7)

pred = model.predict(dtest)
pred = np.exp(pred) - 1
#end::ex_xgb_train_plot_importance


# In[61]:





# In[62]:





# In[63]:





# In[64]:




