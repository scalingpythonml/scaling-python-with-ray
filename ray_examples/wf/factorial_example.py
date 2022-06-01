from ray import workflow
 
@workflow.step
def factorial(n: int) -> int:
    if n == 1:
        return 1
    else:
        return mult.step(n, factorial.step(n - 1))
 
@workflow.step
def mult(a: int, b: int) -> int:
    return a * b
 
# Calculate the factorial of 5 by creating a recursion of 5 steps
factorial_workflow = factorial.step(5).run()
assert factorial_workflow.run() == 120