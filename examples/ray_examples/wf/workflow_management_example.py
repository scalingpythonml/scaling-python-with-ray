from ray import workflow
import ray
 
@workflow.virtual_actor
class Counter:
    def __init__(self, init_val):
        self._val = init_val
 
    def incr(self, val=1):
        self._val += val
        print(self._val)
 
    @workflow.virtual_actor.readonly
    def value(self):
        return self._val
 
workflow.init()
 
# Initialize a Counter actor with id="my_counter".
counter = Counter.get_or_create("my_counter", 0)
 
# Similar to workflow steps, actor methods support:
# - `run()`, which will return the value
# - `run_async()`, which will return a ObjectRef
counter.incr.run(10)
assert counter.value.run() == 10
 
# Non-blocking execution.
counter.incr.run_async(10)
counter.incr.run(10)
assert 30 == ray.get(counter.value.run_async())