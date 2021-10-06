import ray
from time import sleep

# Start Ray
ray.init()

@ray.remote
def remote_function(n: int):
    sleep(n)
    return n

functions = {}
ids = []
id = remote_function.remote(5)
functions[id] = 'func1'
ids.append(id)
id = remote_function.remote(3)
functions[id] = 'func2'
ids.append(id)
id = remote_function.remote(5)
functions[id] = 'func3'
ids.append(id)
id = remote_function.remote(1)
functions[id] = 'func4'
ids.append(id)
id = remote_function.remote(3)
functions[id] = 'func5'
ids.append(id)

while True:
    ready, not_ready = ray.wait(ids)
    print(f'Ready length {len(ready)}; not ready length {len(not_ready)}')
    for id in ready:
        print(f'completed function {functions[id]}, result {ray.get(id)}')
        # Ready results processing goes here
    ids = not_ready
    if not ids:
        break