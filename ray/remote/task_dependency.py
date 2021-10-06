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
def sum_values(v1: int, v2: int, v3: int) -> int :
    return v1+v2+v3

# generate numbers
v1 = generate_number.remote(1, 10, .1)
v2 = generate_number.remote(5, 20, .2)
v3 = generate_number.remote(7, 15, .3)

# get result
print(ray.get(sum_values.remote(v1, v2, v3)))