import ray
from ray.util import ActorPool
from .satelite import SateliteClient


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
# Schedule some of the mail actors, since Kube services doesn't let us dynamically
# bind different ports we only want to do one per-host, but we avoid STRICT_SPREAD
# because of the automatic placement restrictions.
mail_pg = ray.util.placement_group.placement_group(
    strategy="SPREAD",
    lifetime="detached")
