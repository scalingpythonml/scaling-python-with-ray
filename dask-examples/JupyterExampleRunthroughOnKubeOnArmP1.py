#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dask
from dask_kubernetes import KubeCluster
import numpy as np


# In[2]:


# Specify a remote deployment using a load blanacer
dask.config.set({"kubernetes.scheduler-service-type": "LoadBalancer"})


# In[3]:


cluster = KubeCluster.from_yaml('worker-spec.yaml', namespace='dask', deploy_mode='remote')


# In[4]:


cluster.adapt(minimum=1, maximum=100)


# In[5]:


# Example usage
from dask.distributed import Client
import dask.array as da

# Connect Dask to the cluster
client = Client(cluster)


# In[6]:


client.scheduler_comm.comm.handshake_info()


# In[7]:


# Create a large array and calculate the mean
array = da.ones((1000, 1000, 1000))
print(array.mean().compute())  # Should print 1.0|


# In[8]:


print(array.mean().compute())


# In[9]:


print(array.sum().compute())


# In[10]:


dir(array)


# In[11]:


np.take(array, indices=[0, 10]).sum().compute()


# In[12]:


from time import sleep

def inc(x):
    sleep(1)
    return x + 1

def add(x, y):
    sleep(1)
    return x + y


# In[13]:


get_ipython().run_cell_magic('time', '', '# This takes three seconds to run because we call each\n# function sequentially, one after the other\n\nx = inc(1)\ny = inc(2)\nz = add(x, y)')


# In[14]:


from dask import delayed


# In[15]:


get_ipython().run_cell_magic('time', '', '# This runs immediately, all it does is build a graph\n\nx = delayed(inc)(1)\ny = delayed(inc)(2)\nz = delayed(add)(x, y)')


# In[16]:


get_ipython().run_cell_magic('time', '', 'z.compute()')


# In[17]:


data = range(1,100)


# In[18]:


results = []

for x in data:
    y = delayed(inc)(x)
    results.append(y)

total = delayed(sum)(results)
print("Before computing:", total)  # Let's see what type of thing total is
result = total.compute()
print("After computing :", result)  # After it's computed


# In[19]:


total.compute()


# In[20]:


def double(x):
    sleep(1)
    return 2 * x

def is_even(x):
    return not x % 2


# In[21]:


get_ipython().run_cell_magic('time', '', 'results = []\nfor x in data:\n    if is_even(x):  # even\n        y = delayed(double)(x)\n    else:          # odd\n        y = delayed(inc)(x)\n    results.append(y)\n\ntotal = delayed(sum)(results)\ntotal.compute()')


# In[22]:


get_ipython().run_cell_magic('time', '', 'results = []\nfor x in data:\n    def compute(x):\n        if is_even(x):  # even\n            return double(x)\n        else:          # odd\n            return inc(x)\n    y = delayed(compute)(x)\n    results.append(y)\n\ntotal = delayed(sum)(results)\ntotal.compute()')


# In[23]:


total.visualize()


# In[24]:


from dask import compute


# In[25]:


import dask.bag as db
b = db.from_sequence(range(1,100))


# In[26]:


iseven = lambda x: x % 2 == 0


# In[27]:


add = lambda x, y: x + y


# In[28]:


dict(b.foldby(iseven, add))


# In[29]:


b.foldby(iseven, add)


# In[30]:


b.foldby(iseven, add).compute()


# In[31]:


grouped = b.groupby(iseven)


# In[58]:


badsum = grouped.map(lambda kv: (kv[0], sum(kv[1])))


# In[41]:


f = client.scatter(badsum)


# In[42]:


f


# In[45]:


# Note I killed the worker in between
f


# In[59]:


f = client.scatter(badsum)


# In[51]:


f


# In[49]:


dict(f.result())


# In[55]:


# introduced network failure
f.result()


# In[56]:


f


# In[34]:


from bokeh.io import output_notebook, push_notebook
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, show
import numpy as np
output_notebook()

# set up plot background
N = 500
x = np.linspace(-5, 5, N)
y = np.linspace(-5, 5, N)
xx, yy = np.meshgrid(x, y)
d = (1 - xx)**2 + 2 * (yy - xx**2)**2
d = np.log(d)

p = figure(x_range=(-5, 5), y_range=(-5, 5))
p.image(image=[d], x=-5, y=-5, dw=10, dh=10, palette="Spectral11");


# In[35]:


c = client
# a simple function with interesting minima
import time

def rosenbrock(point):
    """Compute the rosenbrock function and return the point and result"""
    time.sleep(0.1)
    score = (1 - point[0])**2 + 2 * (point[1] - point[0]**2)**2
    return point, score


# In[36]:


from dask.distributed import as_completed
from random import uniform

scale = 5                  # Intial random perturbation scale
best_point = (0, 0)        # Initial guess
best_score = float('inf')  # Best score so far
startx = [uniform(-scale, scale) for _ in range(10)]
starty = [uniform(-scale, scale) for _ in range(10)]

# set up plot
source = ColumnDataSource({'x': startx, 'y': starty, 'c': ['grey'] * 10})
p.circle(source=source, x='x', y='y', color='c')
t = show(p, notebook_handle=True)

# initial 10 random points
futures = [c.submit(rosenbrock, (x, y)) for x, y in zip(startx, starty)]
iterator = as_completed(futures)

# TODO(holden): non-blocking?
for res in iterator:
    # take a completed point, is it an improvement?
    point, score = res.result()
    if score < best_score:
        best_score, best_point = score, point
        print(score, point)

    x, y = best_point
    newx, newy = (x + uniform(-scale, scale), y + uniform(-scale, scale))

    # update plot
    source.stream({'x': [newx], 'y': [newy], 'c': ['grey']}, rollover=20)
    push_notebook(document=t)

    # add new point, dynamically, to work on the cluster
    new_point = c.submit(rosenbrock, (newx, newy))
    iterator.add(new_point)  # Start tracking new task as well

    # Narrow search and consider stopping
    scale *= 0.99
    if scale < 0.001:
        break
point


# In[37]:


dir(c)


# In[38]:


help(c)


# In[39]:


c.list_datasets()


# In[60]:


client


# In[62]:





# In[63]:


f


# In[ ]:




