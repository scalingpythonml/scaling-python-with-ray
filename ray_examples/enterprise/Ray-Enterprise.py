#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ray
ray.init(num_cpus=4)


# In[14]:


#tag::ray_metrics_singleton[]
# Singleton for reporting a Ray metric

class FailureCounter(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(FailureCounter, cls).__new__(cls)
            from ray.util.metrics import Counter
            cls._instance.counter = Counter(
                "failure",
                description="Number of failures (goes up only).")
        return cls._instance

# This will fail with every zero because divide by zero
@ray.remote
def remote_fun(x):
    try:
        return 10 / x
    except:
        FailureCounter().counter.inc()
        return None
#end::ray_metrics_singleton[]


# In[17]:


ray.get(remote_fun.remote(0))


# In[32]:


#tag::ray_metrics_actor[]
# Singleton for reporting a Ray metric

@ray.remote
class MySpecialActor(object):
    def __init__(self, name):
        self.total = 0
        from ray.util.metrics import Counter, Gauge
        self.failed_withdrawls = Counter(
            "failed_withdrawls", description="Number of failed withdrawls.",
            tag_keys=("actor_name",), # Useful if you end up sharding actors
        )
        self.failed_withdrawls.set_default_tags({"actor_name": name})
        self.total_guage = Gauge(
            "money",
            description="How much money we have in total. Goes up and down.",
            tag_keys=("actor_name",), # Useful if you end up sharding actors
        )
        self.total_guage.set_default_tags({"actor_name": name})
        self.accounts = {}

    def deposit(self, account, amount):
        if account not in self.accounts:
            self.accounts[account] = 0
        self.accounts[account] += amount
        self.total += amount
        self.total_guage.set(self.total)
        
    def withdrawl(self, account, amount):
        if account not in self.accounts:
            self.failed_withdrawls.inc()
            raise Exception("No account")
        if self.accounts[account] < amount:
            self.failed_withdrawls.inc()
            raise Exception("Not enough money")
        self.accounts[account] -= amount
        self.total -= amount
        self.total_guage.set(self.total)
#end::ray_metrics_actor[]


# In[33]:


bank1 = MySpecialActor.remote("bank1")


# In[34]:


ray.get(bank1.deposit.remote("boo", 5))


# In[35]:


ray.get(bank1.withdrawl.remote("holden", 5))


# In[36]:


ray.get(bank1.withdrawl.remote("boo", 5))


# In[ ]:




