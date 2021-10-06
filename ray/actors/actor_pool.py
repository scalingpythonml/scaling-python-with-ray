import ray
from uuid import uuid4
from time import sleep
from ray.util import ActorPool

# Start Ray
ray.init()

@ray.remote
class PoolActor:
    def __init__(self):
        self.id = str(uuid4())

    def computation(self, num):
        print(f'Actor with id {self.id} waiting for {num} sec')
        for x in range(num):
            sleep(1)
            print(f'Actor with id {self.id} slept for {x} sec')
        return num

# Create actors and add them to the pool
a1, a2, a3 = PoolActor.remote(), PoolActor.remote(), PoolActor.remote()
pool = ActorPool([a1, a2, a3])

print(list(pool.map(lambda a, v: a.computation.remote(v), [3, 4, 5, 4])))

pool.submit(lambda a, v: a.computation.remote(v), 3)
pool.submit(lambda a, v: a.computation.remote(v), 4)
pool.submit(lambda a, v: a.computation.remote(v), 5)
pool.submit(lambda a, v: a.computation.remote(v), 4)

print(pool.get_next())
print(pool.get_next())
print(pool.get_next())
print(pool.get_next())

