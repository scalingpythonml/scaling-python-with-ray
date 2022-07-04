from .satelite import *

def make_satelite_actor(idx):
    return (SateliteClient.options(name=f"satelite_{idx}")
            .remote(idx, actor_count))
actor_count = 10
actor_idx = list(range(0, actor_count))
actors = list(map(make_satelite_actor, actor_idx))
# Since the satelite actors are polling, start them running.
for actor in actors:
    actor.run.remote()
satelite_pool = ActorPool(actors)
