from ray import workflow

@ray.remote
def do_add(a, b):
    return a + b
 
@workflow.step
def add(a, b):
    return do_add.remote(a, b)
 
add.step(ray.put(10), ray.put(20)).run() == 30