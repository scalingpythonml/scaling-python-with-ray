import ray
from ray import serve
import requests

# Start Ray
ray.init()

# Start Serve
serve.start()
#define deployment
@serve.deployment
class Converter:
    def __call__(self, request):
        if request.query_params["type"] == 'CF' :
            return {"Fahrenheit temperature": 9.0/5.0 * float(request.query_params["temp"]) + 32.0}
        elif request.query_params["type"] == 'FC' :
            return {"Celsius temperature": (float(request.query_params["temp"]) - 32.0) * 5.0/9.0 }
        else:
            return {"Unknown conversion code" : request.query_params["type"]}
    def celcius_fahrenheit(self, temp):
        return 9.0/5.0 * temp + 32.0

    def fahrenheit_celcius(self, temp):
        return (temp - 32.0) * 5.0/9.0

Converter.deploy()
# list current deploymente
print(serve.list_deployments())


# Query our endpoint over HTTP.
print(requests.get("http://127.0.0.1:8000/Converter?temp=100.0&type=CF").text)
print(requests.get("http://127.0.0.1:8000/Converter?temp=100.0&type=FC").text)
print(requests.get("http://127.0.0.1:8000/Converter?temp=100.0&type=CC").text)

#direct invoke
from starlette.requests import Request
handle = serve.get_deployment('Converter').get_handle()


print(ray.get(handle.remote(Request({"type": "http", "query_string": b"temp=100.0&type=CF"}))))
print(ray.get(handle.remote(Request({"type": "http", "query_string": b"temp=100.0&type=FC"}))))
print(ray.get(handle.remote(Request({"type": "http", "query_string": b"temp=100.0&type=CC"}))))


print(ray.get(handle.celcius_fahrenheit.remote(100.0)))
print(ray.get(handle.fahrenheit_celcius.remote(100.0)))