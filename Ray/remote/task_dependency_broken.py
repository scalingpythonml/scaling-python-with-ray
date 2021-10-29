import ray
from time import sleep
from random import seed
from random import randint

# Start Ray
ray.init()

@ray.remote
def generate_number(s: int, limit: int, sl: float) -> int :
    seed(s)
    sleep(sl)
    return randint(0, limit)

@ray.remote
def sum_values(values: []) -> int :
    return sum(values)

# get result
print(ray.get(sum_values.remote([generate_number.remote(1, 10, .1),
        generate_number.remote(5, 20, .2), generate_number.remote(7, 15, .3)])))