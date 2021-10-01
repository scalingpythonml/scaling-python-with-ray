import ray
from time import sleep

# Start Ray
ray.init()

@ray.remote
def remote_function(n: int):
    sleep(n)
    return n

execution_time = range(5, 30, 5) # 5, 10, ...
ids = [remote_function.remote(i) for i in execution_time]   # Each waits progressively longer
for x in list(zip(execution_time, ids)):                    # Show what we have, a list of ids and the times each one will take
    print(x)

while True:
    ready, not_ready = ray.wait(ids)
    print('Ready length, values: ', len(ready), ray.get(ready))
    # Ready results processing goes here
    print('Not Ready length:', len(not_ready))
    ids = not_ready
    if not ids:
        break