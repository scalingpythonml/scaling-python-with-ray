#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from typing import Tuple
import ray
ray.init(num_cpus=20) # In theory auto sensed, in practice... eh


# In[ ]:


import sys
import time
import timeit
import threading
import random


# In[ ]:



#tag::variable_sleep_task[]
@ray.remote
def remote_task(x):
    time.sleep(x)
    return x
#end::variable_sleep_task[]

things = list(range(10))
things.sort(reverse=True)


# In[ ]:


#tag::get_only[]
# Process in order
def in_order():
    # Make the futures
    futures = list(map(lambda x: remote_task.remote(x), things))
    values = ray.get(futures)
    for v in values:
        print(f" Completed {v}")
        time.sleep(1) # Business logic goes here
#end::get_only[]


# In[ ]:


# Does not work - TypeError: get() takes 1 positional argument but 10 were given
#tag::get_only_splat[]
# Make the futures
#futures = map(lambda x: remote_task.remote(x), things)
#values = ray.get(*futures)
#for v in values:
#    print(f" Completed {v}")
#tag::get_only_splat[]


# In[ ]:


# Currently ray.wait will not return more than num_returns objects as ready
# even if there are. This might change so even when fetching an object at a time
# iterate over the result.
#tag::as_available[]
# Process as results become available
def as_available():
    # Make the futures
    futures = list(map(lambda x: remote_task.remote(x), things))
    # While we still have pending futures
    while len(futures) > 0:
        ready_futures, rest_futures = ray.wait(futures)
        print(f"Ready {len(ready_futures)} rest {len(rest_futures)}")
        for id in ready_futures:
            print(f'completed value {id}, result {ray.get(id)}')
            time.sleep(1) # Business logic goes here
        # We just need to wait on the ones which are not yet available
        futures = rest_futures
#end::as_available[]


# In[ ]:


timeit.timeit(lambda: as_available(), number=1)


# In[ ]:


timeit.timeit(lambda: in_order(), number=1)


# In[ ]:


#tag::handle_bad_futures[]
futures = list(map(lambda x: remote_task.remote(x), [1, threading.TIMEOUT_MAX]))
# While we still have pending futures
while len(futures) > 0:
    # In practice 10 seconds is too short for most cases.
    ready_futures, rest_futures = ray.wait(futures, timeout=10, num_returns=1)
    # If we get back anything less than num_returns 
    if len(ready_futures) < 1:
        print(f"Timed out on {rest_futures}")
        # You don't _have to cancel_ but if you've your task is using a lot of resources
        ray.cancel(*rest_futures)
        # You should break since you exceeded your timeout
        break
    for id in ready_futures:
        print(f'completed value {id}, result {ray.get(id)}')
        futures = rest_futures
#end::handle_bad_futures[]


# In[ ]:


remote_task.remote(1)


# In[ ]:


#tag::ray_remote_seq[]
@ray.remote
def generate_number(s: int, limit: int, sl: float) -> int :
   random.seed(s)
   time.sleep(sl)
   return random.randint(0, limit)

@ray.remote
def sum_values(v1: int, v2: int, v3: int) -> int :
   return v1+v2+v3

# get result
print(ray.get(sum_values.remote(generate_number.remote(1, 10, .1),
       generate_number.remote(5, 20, .2), generate_number.remote(7, 15, .3))))
#end::ray_remote_seq[]


# In[ ]:


# Does not work -- Ray won't resolve any nested ObjectRefs
#tag::broken_ray_remote_seq[]
@ray.remote
def generate_number(s: int, limit: int, sl: float) -> int :
   random.seed(s)
   time.sleep(sl)
   return random.randint(0, limit)

@ray.remote
def sum_values(values: []) -> int :
   return sum(values)

# get result
print(ray.get(sum_values.remote([generate_number.remote(1, 10, .1),
       generate_number.remote(5, 20, .2), generate_number.remote(7, 15, .3)])))
#end::broken_ray_remote_seq[]


# In[ ]:


#tag::ray_no_pipeline[]
@ray.remote
def generate_number(s: int, limit: int, sl: float) -> int :
   random.seed(s)
   time.sleep(sl)
   return random.randint(0, limit)

@ray.remote
def sum_values(values: []) -> int :
   return sum(ray.get(values))

# get result
print(ray.get(sum_values.remote([generate_number.remote(1, 10, .1),
       generate_number.remote(5, 20, .2), generate_number.remote(7, 15, .3)])))
#end::ray_no_pipeline[]


# In[ ]:


#tag::nested_par[]
@ray.remote
def generate_number(s: int, limit: int) -> int :
   random.seed(s)
   time.sleep(.1)
   return randint(0, limit)

@ray.remote
def remote_objrefs():
   results = []
   for n in range(4):
       results.append(generate_number.remote(n, 4*n))
   return results

@ray.remote
def remote_values():
   results = []
   for n in range(4):
       results.append(generate_number.remote(n, 4*n))
   return ray.get(results)

print(ray.get(remote_values.remote()))
futures = ray.get(remote_objrefs.remote())
while len(futures) > 0:
    ready_futures, rest_futures = ray.wait(futures, timeout=600, num_returns=1)
    # If we get back anything less than num_returns there was a timeout
    if len(ready_futures) < 1:
        ray.cancel(*rest_futures)
        break
    for id in ready_futures:
        print(f'completed result {ray.get(id)}')
        futures = rest_futures
#end::nested_par[]


# In[ ]:


#tag::bring_it_together_with_ensemble[]
import random

@ray.remote
def fetch(url: str) -> Tuple[str, str]:
    import urllib.request
    with urllib.request.urlopen(url) as response:
       return (url, response.read())

@ray.remote
def has_spam(site_text: Tuple[str, str]) -> bool:
    # Open the list of spammers or download it
    spammers_url = "https://raw.githubusercontent.com/matomo-org/referrer-spam-list/master/spammers.txt"
    import urllib.request
    with urllib.request.urlopen(spammers_url) as response:
            spammers = response.readlines()
            for spammer in spammers:
                if spammer in site_text[1]:
                    return True
    return False
            
    
@ray.remote
def fake_spam1(us: Tuple[str, str]) -> bool:
    # You should do something fancy here with TF or even just NLTK
    time.sleep(10)
    if random.randrange(10) == 1:
        return True
    else:
        return False
    
@ray.remote
def fake_spam2(us: Tuple[str, str]) -> bool:
    # You should do something fancy here with TF or even just NLTK
    time.sleep(5)
    if random.randrange(10) > 4:
        return True
    else:
        return False
    
@ray.remote
def combine_is_spam(us: Tuple[str, str], model1: bool, model2: bool, model3: bool) -> Tuple[str, str, bool]:
    # Questionable fake ensemble
    score = model1 * 0.2 + model2 * 0.4 + model3 * 0.4
    if score > 0.2:
        return True
    else:
        return False
#end::bring_it_together_with_ensemble[]


# In[ ]:


urls = ["http://www.unitedwifi.com", "http://www.google.com", "http://www.holdenkarau.com"]
site_futures = map(lambda url: fetch.remote(url), urls)
spam_futures = map(lambda us: [us, has_spam.remote(us), fake_spam1.remote(us), fake_spam2.remote(us)],
                   site_futures)
info_futures = map(lambda i: combine_is_spam.remote(*i), spam_futures)
                   
                   
not_ready = list(info_futures)
while len(not_ready) > 0:
    ready, not_ready = ray.wait(not_ready, num_returns = 1)
    if len(ready) < 1:
        raise Exception("Error fetching futures")
    print(ray.get(ready))

