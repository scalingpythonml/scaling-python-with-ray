import ray
import time
from time import sleep

# Start Ray
ray.init()

# A regular Python function.
def regular_function(n: int):
    print(f'Starting function {n}')
    sleep(1)
    print(f'Completing function {n}')
    return 1

# A Ray remote function.
@ray.remote
def remote_function(n: int):
    print(f'Starting function {n}')
    sleep(1)
    print(f'Completing function {n}')
    return 1

# invoking regular function
result = 0
start = time.time()
for n in range(4):
    result += regular_function(n)
print(f'Execution result {result} in {time.time() - start}')

# invoking remote function
results = []
start = time.time()
for n in range(4):
    results.append(remote_function.remote(n))
print(f'Execution result {sum(ray.get(results))} in {time.time() - start}')