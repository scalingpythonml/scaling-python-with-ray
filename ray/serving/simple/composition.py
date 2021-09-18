from random import random
import requests
import ray
from ray import serve

ray.init()
serve.start()

@serve.deployment
def model_one(data):
    return {"result": "model1"}


model_one.deploy()


@serve.deployment
def model_two(data):
    return {"result": "model2"}


model_two.deploy()

# max_concurrent_queries is optional. By default, if you pass in an async
# function, Ray Serve sets the limit to a high number.
@serve.deployment(route_prefix="/model")
class Canary:
    def __init__(self, canary_percent):
        from random import random
        self.model_one = model_one.get_handle()
        self.model_two = model_two.get_handle()
        self.canary_percent = canary_percent

    # This method can be called concurrently!
    async def __call__(self, request):
        data = await request.body()
        if(random() < self.canary_percent):
            return await self.model_one.remote(data=data)
        else:
            return await self.model_two.remote(data=data)

Canary.deploy(.3)

for _ in range(10):
    resp = requests.get("http://127.0.0.1:8000/model", data="hey!")
    print(resp.json())