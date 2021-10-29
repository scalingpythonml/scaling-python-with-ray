import ray
from time import sleep

ray.init()

@ray.remote
class ThreadedActor:
    def computation(self, num):
        print(f'Actor waiting for {num} sec')
        for x in range(num):
            sleep(1)
            print(f'Actor slept for {x+1} sec')
        return num

actor = ThreadedActor.options(max_concurrency=3).remote()

r1, r2, r3 = ray.get([actor.computation.remote(3),
                      actor.computation.remote(5), actor.computation.remote(2)])

print(r1, r2, r3)
