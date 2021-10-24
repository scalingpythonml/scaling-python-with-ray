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
    return regular_function(n)

# invoking regular function
print(f'Executing regular function {regular_function(1)}')
start = time.time()
result = sum([regular_function(n) for n in range(4)])
print(f'Regular function. Execution result {result} in {time.time() - start}')

# invoking remote function
result = remote_function.remote(1)
print(f'Executing remote function {result} result {ray.get(result)}')
start = time.time()
results = [remote_function.remote(n) for n in range(4)]
print(f'Execution result {sum(ray.get(results))} in {time.time() - start}')