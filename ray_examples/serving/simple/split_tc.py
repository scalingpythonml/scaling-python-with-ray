import ray
from ray import serve
from fastapi import FastAPI
import requests

# Strat Fast APIs
app = FastAPI()
# Start Ray
ray.init()

# Start Serve
serve.start()
#define deployment
#tag::deploy[]
@serve.deployment(route_prefix="/converter")
@serve.ingress(app)
class Converter:
    @app.get("/cf")
    def celcius_fahrenheit(self, temp):
        return {"Fahrenheit temperature": 9.0/5.0 * float(temp) + 32.0}

    @app.get("/fc")
    def fahrenheit_celcius(self, temp):
        return {"Celsius temperature": (float(temp) - 32.0) * 5.0/9.0}
#end::deploy[]

Converter.deploy()
# list current deploymente
print(serve.list_deployments())


# Query our endpoint over HTTP.
#tag::call_multi[]
print(requests.get("http://127.0.0.1:8000/converter/cf?temp=100.0&").text)
print(requests.get("http://127.0.0.1:8000/converter/fc?temp=100.0").text)
#end::call_multi[]

#direct invoke
handle = serve.get_deployment('Converter').get_handle()

print(ray.get(handle.celcius_fahrenheit.remote(100.0)))
print(ray.get(handle.fahrenheit_celcius.remote(100.0)))
