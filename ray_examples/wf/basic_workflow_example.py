import ray
from ray import workflow
from typing import List
 
# Creating an arbitrary Ray remote function 
@ray.remote
def hello():
    return "hello"
 
# Defining a workflow step that puts an object into the object store
@workflow.step
def words() -> List[ray.ObjectRef]:
    return [hello.remote(), ray.put("world")]
 
# Defining a step that receives an object
@workflow.step
def concat(words: List[ray.ObjectRef]) -> str:
    return " ".join([ray.get(w) for w in words])

# Creating workflow
workflow.init("tmp/workflow_data")
output: "Workflow[int]" = concat.step(words.step())

# Running workflow
assert output.run(workflow_id="workflow_1") == "hello world"
assert workflow.get_status("workflow_1") == workflow.WorkflowStatus.SUCCESSFUL
assert workflow.get_output("workflow_1") == "hello world"