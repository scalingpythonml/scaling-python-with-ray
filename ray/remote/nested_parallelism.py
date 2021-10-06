import ray
from time import sleep
from random import seed
from random import randint

# Start Ray
ray.init()

@ray.remote
def generate_number(s: int, limit: int) -> int :
    seed(s)
    sleep(.1)
    return randint(0, limit)

@ray.remote
def remote_objrefs():
    # Call f 4 times and return the resulting object IDs.
    results = []
    for n in range(4):
        results.append(generate_number.remote(n, 10*n))
    return results

@ray.remote
def remote_values():
    # Call f 4 times, block until those 4 tasks finish,
    # retrieve the results, and return the values.
    results = []
    for n in range(4):
        results.append(generate_number.remote(n, 10*n))
    return ray.get(results)

print(ray.get(remote_objrefs.remote()))
print(ray.get(remote_values.remote()))
