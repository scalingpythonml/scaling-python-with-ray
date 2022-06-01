from ray import workflow 

@workflow.virtual_actor
class counter:
    def __init__(self):
        self.count = 0
 
    def incr(self):
        self.count += 1
        return self.count
 
workflow.init(storage="/tmp/workflows")
 

workflow1 = counter.get_or_create("counter_workflw")
assert c1.incr.run() == 1
assert c1.incr.run() == 2