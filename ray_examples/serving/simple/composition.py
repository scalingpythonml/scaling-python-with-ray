from random import random
import requests
import ray
from ray import serve

ray.init()
serve.start()

@serve.deployment
def version_one(data):
    return {"result": "version1"}


version_one.deploy()


@serve.deployment
def version_two(data):
    return {"result": "version2"}


version_two.deploy()

# max_concurrent_queries is optional. By default, if you pass in an async
# function, Ray Serve sets the limit to a high number.
@serve.deployment(route_prefix="/versioned")
class Canary:
    def __init__(self, canary_percent):
        from random import random
        self.version_one = version_one.get_handle()
        self.version_two = version_two.get_handle()
        self.canary_percent = canary_percent

    # This method can be called concurrently!
    async def __call__(self, request):
        data = await request.body()
        if(random() < self.canary_percent):
            return await self.version_one.remote(data=data)
        else:
            return await self.version_two.remote(data=data)

Canary.deploy(.3)

for _ in range(10):
    resp = requests.get("http://127.0.0.1:8000/versioned", data="hey!")
    print(resp.json())