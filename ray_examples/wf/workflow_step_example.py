from ray import workflow
 
@workflow.step
def sum(x: int, y: int, z: int) -> int:
    return x + y + z
 
@workflow.step
def get_value1() -> int:
    return 100
 
@workflow.step
def get_value2(x: int) -> int:
    return 10*x
 
sum_workflow = sum.step(get_value1.step(), get_value2.step(10), 100)
 
assert sum_workflow.run("sum_example") == 300