from ray import workflow
import ray
 
@workflow.step
def double(s):
    return 2 * s
 
@workflow.virtual_actor
class Actor:
    def __init__(self):
        self.val = 1
 
    def double(self, update):
        step = double.step(self.val)
        if not update:
            # inside the method, a workflow can be launched
            return step
        else:
            # workflow can also be passed to another method
            return self.update.step(step)
 
    def update(self, v):
        self.val = v
        return self.val
 
 
handler = Actor.get_or_create("actor")
assert handler.double.run(False) == 2
assert handler.double.run(False) == 2
assert handler.double.run(True) == 2
assert handler.double.run(True) == 4