from ray import workflow 

@workflow.step
def add(a: int, b: int) -> int:
    return a + b

@workflow.step
def fib(n: int) -> int:
    if n <= 1:
        return n
    return add.step(fib.step(n - 1), fib.step(n - 2))

assert fib.step(10).run() == 55