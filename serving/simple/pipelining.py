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
@serve.deployment(max_concurrent_queries=10, route_prefix="/model")
class Canary:
    def __init__(self):
        from random import random
        self.model_one = model_one.get_handle()
        self.model_two = model_two.get_handle()

    # This method can be called concurrently!
    async def __call__(self, starlette_request):
        data = await starlette_request.body()
        if(random() < .3):
            return await self.model_one.remote(data=data)
        else:
            return await self.model_two.remote(data=data)

Canary.deploy()

for _ in range(10):
    resp = requests.get("http://127.0.0.1:8000/model", data="hey!")
    print(resp.json())