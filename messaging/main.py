import time
import ray
from ray.util import ActorPool
from messaging.satellite.satellite import SatelliteClient
from messaging.mailserver.mailserver_actor import MailServerActor
from messaging.users.user_actor import UserActor


def do_launch(actor_count: int, grace_period: int = 240):
    """
    Launch the sect of actors that serve as the backend for the SpaceBeaver project.
    """
    actor_idxs = list(range(0, actor_count))

    # semi-gracefully shut down existing actors. Here we depend on a two facts:
    # 1) There is an (external to Ray) mailserver which will queue messages for us.
    # 2) Satellite API is polling not push (no harm to shutdown).
    actors_found = 0
    for actor_name in ["mailserver", "satellite", "user"]:
        for i in actor_idxs:
            try:
                a = ray.get_actor(f"{actor_name}_{i}")
                actors_found += 1
                a.prepare_for_shutdown.remote()
            except Exception:
                pass
    if actors_found > 0:
        time.sleep(grace_period)
        for actor_name in ["mailserver", "satellite", "user"]:
            for i in actor_idxs:
                try:
                    a = ray.get_actor(f"{actor_name}_{i}")
                    ray.kill(a)
                except Exception:
                    pass

    def make_satellite_actor(idx: int):
        return (SatelliteClient.options(name=f"satellite_{idx}")  # type: ignore
                .remote(idx, actor_count))

    satellite_actors = list(map(make_satellite_actor, actor_idxs))
    # Since the satellite actors are polling, start them running.
    for actor in satellite_actors:
        actor.run.remote()
    satellite_pool = ActorPool(satellite_actors)

    def make_user_actor(idx: int):
        return (UserActor.options(name=f"user_{idx}")  # type: ignore
                .remote(idx, actor_count))

    user_actors = list(map(make_user_actor, actor_idxs))
    user_pool = ActorPool(user_actors)

    # Schedule some of the mail actors, since Kube services doesn't let us dynamically
    # bind different ports we only want to do one per-host, but we avoid STRICT_SPREAD
    # because of the automatic placement restrictions.
    mailserver_resources = list(map(lambda x: {"CPU": 0.1}, actor_idxs))
    mailserver_pg = ray.util.placement_group(
        mailserver_resources,
        strategy="SPREAD",
        lifetime="detached")

    def make_mailserver_actor(idx: int):
        return (MailServerActor  # type: ignore
                .options(
                    name=f"mailserver_{idx}",
                    placement_group=mailserver_pg,
                    num_cpus=0.1,
                    lifetime="detached")
                .remote(
                    idx=idx,
                    poolsize=actor_count,
                    port=7420,
                    hostname="spacebeaver.com",
                    label="mail_ingress"))

    mailserver_actors = list(map(make_mailserver_actor, actor_idxs))
    mailserver_pool = ActorPool(mailserver_actors)

    return (satellite_pool, mailserver_pool, user_pool)


if __name__ == "__main__":
    do_launch(actor_count=2)
