import ray
import os
import requests
import qiskit
import argparse

class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kwargs', nargs='*', action=ParseKwargs)
args = parser.parse_args()

numberOfIterations = int(args.kwargs["iterations"])
print(f"Requested number of iterations is: {numberOfIterations}")

print(f'environment variable MY_VARIABLE1 has a value of {os.getenv("MY_VARIABLE1")}, '
      f'MY_VARIABLE2 has a value of {os.getenv("MY_VARIABLE2")}')

ray.init()

@ray.remote
class Counter:
    def __init__(self):
        self.counter = 0

    def inc(self):
        self.counter += 1

    def get_counter(self):
        return self.counter

counter = Counter.remote()

for _ in range(numberOfIterations):
    ray.get(counter.inc.remote())
    print(ray.get(counter.get_counter.remote()))

print("Requests", requests.__version__)
print("Qiskit", qiskit.__version__)
