import ray
from ray import workflow
from typing import List

@workflow.step
def add(values: List[int]) -> int:
    return sum(values)
 
@workflow.step
def get_val() -> int:
    return 10
 
ret = add.step([get_val.step() for _ in range(3)])
assert ret.run() == 30