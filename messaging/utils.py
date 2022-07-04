import ray
from ray.util import ActorPool
import time

def flat_map(f, xs):
    ys = []
    for x in xs:
        ys.extend(f(x))
    return ys

class LazyNamedPool:
    """
    Lazily constructed pool by name.
    """
    def __init__(self, name, size, min_size = 1):
        self._actors = []
        self.name = name
        self.size = size
        self.min_actors = min_size

    def _get_actor(self, idx):
        actor_name = f"{self.name}_{idx}"
        try:
            return [ray.get_actor(actor_name)]
        except Exception as e:
            print(f"Failed to fetch {actor_name}: {e} ({type(e)})")
            return []

    def _get_actors(self):
        if len(self._actors) < self.size:
            return list(flat_map(self._get_actor, range(0, self.size)))

    def get_pool(self):
        new_actors = self._get_actors()
        # Wait for at least min_actors to show up
        while len(new_actors) < self.min_actors:
            print(f"Have {new_actors} waiting for {self.min_actors}")
            time.sleep(1)
            new_actors = self._get_actors()
        # If we got more actors
        if (len(new_actors) > len(self._actors)):
            self._actors = new_actors
            self._pool = ActorPool(new_actors)            
        return self._pool


__all__ = ["flat_map", "LazyNamedPool"]
