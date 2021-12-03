import ray
from ray.util import ActorPool
import time
from time import sleep

from ray.util.placement_group import (
    placement_group,
    PlacementGroup,
    remove_placement_group
)

# Start Ray
print(f'Using Ray version {ray.__version__}')
ray.init("ray://localhost:10001")

# A Ray remote function.
@ray.remote(num_cpus=.1)
def remote_function(n: int):
    sleep(n)
    return

@ray.remote(num_cpus=.1)
def remote_caller(sleep_time: int, number_invokes: int):
    start = time.time()
    results = [remote_function.remote(sleep_time) for n in range(number_invokes)]
    starttime = time.time() - start
    ray.get(results)
    return starttime, time.time() - start

@ray.remote(num_cpus=.1)
def remote_caller_placement(sleep_time: int, number_invokes: int, pg: PlacementGroup):

    start = time.time()
    results = [remote_function.options(placement_group=pg).remote(sleep_time) for n in range(number_invokes)]
    starttime = time.time() - start
    ray.get(results)
    return starttime, time.time() - start

@ray.remote(num_cpus=.1)
def remote_fan(sleep_time: int):
    results = [remote_fan_leaf.remote(sleep_time) for n in range(10)]
    ray.get(results)
    return

@ray.remote(num_cpus=.1)
def remote_fan_leaf(sleep_time: int):
    results = [remote_function.remote(sleep_time) for n in range(10)]
    ray.get(results)
    return

@ray.remote(num_cpus=.1)
def remote_fan_invoker(sleep_time: int, number_invokes: int):
    start = time.time()
    results = [remote_fan.remote(sleep_time) for n in range(number_invokes)]
    ray.get(results)
    return time.time() - start

@ray.remote(num_cpus=.1)
class JobExecutor:
    def computation(self, n: int):
        sleep(n)
        return

@ray.remote
def remote_worker_caller(executor: ActorPool, sleep_time: int, number_invokes: int):
    start = time.time()
    [executor.submit(lambda a, v: a.computation.remote(v), sleep_time) for n in range(number_invokes)]
    starttime = time.time() - start
    while(executor.has_next()):
        executor.get_next()
    return starttime, time.time() - start


# Direct invokes
sleep_time = 5
number_invokes = [10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
#for n in number_invokes:
#    start, execution = ray.get(remote_caller.remote(sleep_time, n))
#    print(f'Executed {n} invocations with sleep {sleep_time} in {execution}s, start time {start}s')

# Hierarchical invokes
#n_invokes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#for n in n_invokes:
#    execution = ray.get(remote_fan_invoker.remote(sleep_time, n))
#    print(f'Executed {n*100} invocations with sleep {sleep_time} in {execution}s')

#Placement groups
# Create a placement group.
#print("Creating placement group")
#start = time.time()
#pg = placement_group([{"CPU": 10}, {"CPU": 10}, {"CPU": 10}, {"CPU": 10}, {"CPU": 10}], strategy="STRICT_SPREAD")
#ray.get(pg.ready())
#print(f"Placement group created {time.time() - start}")

# invoking remote function
#for n in number_invokes:
#    start, execution = ray.get(remote_caller_placement.remote(sleep_time, n, pg))
#    print(f'Executed {n} invocations with sleep {sleep_time} in {execution}s, start time {start}s')

# Delete placement group. This API is asynchronous.
#remove_placement_group(pg)
# Wait until placement group is killed.
#sleep(1)

#using executors

print("Creating Actor pool")
start = time.time()
actors = [JobExecutor.remote() for n in range(500)]
pool = ActorPool(actors)
print(f"Actor pool is created {time.time() - start}")

for n in number_invokes:
    start, execution = ray.get(remote_worker_caller.remote(pool, sleep_time, n))
    print(f'Executed {n} invocations with sleep {sleep_time} in {execution}s, start time {start}s')
