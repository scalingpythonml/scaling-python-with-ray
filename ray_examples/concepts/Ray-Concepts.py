#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ray


# In[ ]:


from typing import *


# In[ ]:


#tag::pip_pkg_reqs[]
runtime_env = {"pip": "requirements.tt"}
#end::pip_pkg_reqs[]


# In[ ]:


#tag::pip_pkg_list[]
runtime_env = {"pip": ["bs4"]}
#end::pip_pkg_list[]


# In[ ]:


if False:
    #tag::ray_obj_store_config[]
    ray.init(num_cpus=20,
         _system_config={
            "min_spilling_size": 1024 * 1024,  # Spill at least 1MB
            "object_store_memory_mb": 500,
            "object_spilling_config": json.dumps(
                {"type": "filesystem", "params": {"directory_path": "/tmp/fast"}},
                )
             })
    #end::ray_obj_store_cofig[]
else:
    #tag::runtime_env_init[]
    ray.init(num_cpus=20, runtime_env=runtime_env)
    #end::runtime_env_init[]


# In[ ]:


#tag::custom_serializer[]
import ray.cloudpickle as pickle
from multiprocessing import Pool
pickle

class BadClass:
    def __init__(self, threadCount, friends):
        self.friends = friends
        self.p = Pool(threadCount) # not serializable

i = BadClass(5, ["boo", "boris"])
# This will fail with a "NotImplementedError: pool objects cannot be passed between processes or pickled"
# pickle.dumps(i)

class LessBadClass:
    def __init__(self, threadCount, friends):
        self.friends = friends
        self.p = Pool(threadCount)
    def __getstate__(self):
        state_dict = self.__dict__.copy()
        # We can't move the threads but we can move the info to make a pool of the same size
        state_dict["p"] = len(self.p._pool)
        return state_dict
    def __setsate__(self):
        self.__dict__.update(state)
        self.p = Pool(self.p)
k = LessBadClass(5, ["boo", "boris"])
pickle.loads(pickle.dumps(k))
#end::custom_serializer[]


# In[ ]:


#tag::custom_serializer_not_own_class[]

def custom_serializer(bad):
    return {"threads": len(bad.p._pool), "friends": bad.friends}

def custom_deserializer(params):
    return BadClass(params["threads"], params["friends"])

# Register serializer and deserializer the BadClass:
ray.util.register_serializer(
  BadClass, serializer=custom_serializer, deserializer=custom_deserializer)
ray.get(ray.put(i))
#end::custom_serializer_not_own_class[]


# In[ ]:


ray.util.inspect_serializability(Pool(5))


# In[ ]:


#tag::flaky_remote_fun[]
@ray.remote
def flaky_remote_fun(x):
    import random
    import sys
    if random.randint(0, 2) == 1:
        sys.exit(0)
    return x

r = flaky_remote_fun.remote(1)
#end::flaky_remote_fun[]


# In[ ]:


ray.get(r)


# In[ ]:


r = flaky_remote_fun.remote(1)


# In[ ]:


ray.get(r)


# In[ ]:


#tag::flaky_remote_fun_exception[]
@ray.remote
def flaky_remote_fun_exception(x):
    import random
    import sys
    if random.randint(0, 2) == 1:
        raise Exception("teapots")
    return x

r = flaky_remote_fun_exception.remote(1)
#end::flaky_remote_fun_exception[]


# In[ ]:


ray.get(flaky_remote_fun_exception.remote(1))


# In[ ]:


#tag::flaky_constructor_actor[]
flaky_constructor_actor = None
@ray.remote(max_restarts=5)
class FlakyActor(object):    
    def __init__(self):
        import random
        import sys
        if random.randint(0, 2) == 1:
            sys.exit(1)
        self.value = 0

    def greet(self):
        self.value += 1
        return f"Hi user #{self.value}"

flaky_constructor_actor = FlakyActor.remote()
#end::flaky_constructor_actor[]


# In[ ]:


j = None
j = ray.get(flaky_constructor_actor.greet.remote())
j


# In[ ]:


j


# In[ ]:


#tag::flaky_in_msg_actor[]
@ray.remote(max_restarts=5)
class FlakyMsgActor(object):    
    def __init__(self):
        import random
        self.value = 0

    def greet(self):
        self.value += 1
        import random
        if random.randint(0, 2) == 1:
            raise Exception("I am a teapot")
        return f"Hi user #{self.value}"

flaky_msg_actor = FlakyMsgActor.remote()
#end::flaky_in_msg_actor[]


# In[ ]:


ray.get(flaky_msg_actor.greet.remote())


# In[ ]:


#tag::flaky_in_msg_crash_actor[]
@ray.remote(max_restarts=5)
class FlakyMsgCrashActor(object):    
    def __init__(self):
        import random
        self.value = 0

    def greet(self):
        self.value += 1
        import random
        if random.randint(0, 3) == 1:
            import sys
            sys.exit(1)
        return f"Hi user #{self.value}"

flaky_msg_crashactor = FlakyMsgCrashActor.remote()
#end::flaky_in_msg_crash_actor[]


# In[ ]:


ray.get(flaky_msg_crashactor.greet.remote())


# In[ ]:


flaky_msg_crashactor.greet.remote()


# In[ ]:


#tag::flaky_inbetween[]
@ray.remote(max_restarts=5)
class FlakyInBetweenActor(object):  
    def __init__(self):
        import random
        import threading
        # Create a backup thread to simulate failure
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True # Daemonize thread
        self.thread.start() # Start the execution
        self.value = 0

    def run(self):
        import time
        time.sleep(4)
        import os, signal
        p = os.getpid()
        # Ray traps SIGINT so use SIGKILL
        os.kill(os.getpid(), signal.SIGKILL)

    def greet(self):
        self.value += 1
        return f"Hi user #{self.value}"

flaky_inbetween_actor = FlakyInBetweenActor.remote()
#end::flaky_inbetween[]


# In[ ]:


import time
results = []
results.append(ray.get(flaky_inbetween_actor.greet.remote()))
results.append(ray.get(flaky_inbetween_actor.greet.remote()))
time.sleep(6) # Sleep long enough to restart
results.append(ray.get(flaky_inbetween_actor.greet.remote()))
results


# In[ ]:


time.sleep(6*5) # Exceed max restarts
results.append(ray.get(flaky_inbetween_actor.greet.remote()))


# In[ ]:


#tag::ex_use_ray_put[]
import numpy as np
@ray.remote
def sup(x):
    import random
    import sys
    return len(x)

p = ray.put(np.array(range(0, 1000)))
ray.get([sup.remote(p), sup.remote(p), sup.remote(p)])
#end::ex_use_ray_put[]


# In[ ]:


#tag::ex_ray_immuteable[]
remote_array = ray.put([1])
v = ray.get(remote_array)
v.append(2)
print(v)
print(ray.get(remote_array))
#end::ex_ray_immuteable[]


# In[ ]:


#tag::placement_group_imports[]
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group
)
#end::placement_group_imports[]


# In[ ]:


@ray.remote
def remote_fun(x):
    return x


# In[ ]:


#tag::placement_group[]
# Create a placement group.
cpu_bundle = {"CPU": 3}
mini_cpu_bundle = {"CPU": 1}
pg = placement_group([cpu_bundle, mini_cpu_bundle])
ray.get(pg.ready())
print(placement_group_table(pg))
print(ray.available_resources())
# Run remote_fun in cpu_bundle
handle = remote_fun.options(placement_group=pg, placement_group_bundle_index=0).remote(1)
#end::placement_group[]


# In[ ]:


#tag::runtime_env_local[]
@ray.remote(runtime_env=runtime_env)
def sup(x):
    from bs4 import BeautifulSoup
#end::runtime_env_local[]


# In[ ]:


#tag::bring_it_together_with_fetch_and_runtime_env[]
runtime_env = {"pip": ["bs4"]}

@ray.remote
def fetch(url: str) -> Tuple[str, str]:
    import urllib.request
    with urllib.request.urlopen(url) as response:
       return (url, response.read())

@ray.remote(runtime_env=runtime_env)
def extract_title(url_text: Tuple[str, str]) -> Tuple[str, str]:
    from bs4 import BeautifulSoup
    html = url_text[1]
    soup = BeautifulSoup(html, 'html.parser')
    return (url_text[0], soup.find('title').get_text())

#tag::pg_ex[]
# Pin the remote function inside the placement group to re-use the spammers URL fetch
# note: you can't specify placement_group_bundle_index here, to use that you need to use
# .options
@ray.remote(placement_group=pg)
def has_spam(site_text: Tuple[str, str]) -> Tuple[str, bool]:
    # Open the list of spammers or download it
    spammers_url = "https://raw.githubusercontent.com/matomo-org/referrer-spam-list/master/spammers.txt"
    spammers = []
    try:
        with open("spammers.txt", "r") as spammers_file:
            spammers = spammers_file.readlines()
    except:
        import urllib.request
        with urllib.request.urlopen(spammers_url) as response:
            with open("spammers.txt", "w") as spammers_file:
                spammers = response.text.split("\n")
                spammers_file.writelines(spammers)
    for s in spammers:
        if s in site_text[1]:
            return True
    return False
#end::pg_ex[]        

urls = ["http://www.holdenkarau.com", "http://www.google.com"]
# Turn this into a list since we are consuming it twice downstream.
site_futures = list(map(lambda url: fetch.remote(url), urls))
info_futures = map(lambda pf: extract_title.remote(pf), site_futures)
spammer_futures = map(lambda pf: has_spam.remote(pf), site_futures)

not_ready = list(info_futures)
not_ready.extend(spammer_futures)
while len(not_ready) > 0:
    ready, not_ready = ray.wait(not_ready, num_returns = 1)
    if len(ready) < 1:
        raise Exception("Error fetching futures")
    print(ray.get(ready))
#end::bring_it_together_with_fetch_and_runtime_env[]

