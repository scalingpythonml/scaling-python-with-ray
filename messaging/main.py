import time
import ray
from ray.util import ActorPool
from messaging.satellite.satellite import SatelliteClient
from messaging.mailserver.mailserver_actor import MailServerActor
from messaging.users.user_actor import UserActor
from messaging.settings.settings import Settings


def do_launch(actor_count: int, grace_period: int = 240):
    """
    Launch the sect of actors that serve as the backend for the SpaceBeaver project.
    """
    print(f"Launching actors (parallelism {actor_count}")
    settings = Settings()
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
        return (SatelliteClient.options(  # type: ignore
            name=f"satellite_{idx}",
            max_task_retries=settings.max_retries)
            .remote(settings, idx, actor_count))

    satellite_actors = list(map(make_satellite_actor, actor_idxs))
    # Since the satellite actors are polling, start them running.
    for actor in satellite_actors:
        actor.run.remote()
    satellite_pool = ActorPool(satellite_actors)

    def make_user_actor(idx: int):
        return (UserActor.options(name=f"user_{idx}")  # type: ignore
                .remote(settings, idx, actor_count))

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
                    lifetime="detached",
                    max_task_retries=settings.max_retries)
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
    import argparse
    parser = argparse.ArgumentParser(description='Handle some satellite messags')
    parser.add_argument('--ray-head', type=str, required=False,
                        help='Head node to submit to')
    parser.add_argument('--actor-count', type=int, default=2,
                        required=False, help='number of actors')
    args = parser.parse_args()
    if args.ray_head is not None:
        ray.init(args.ray_head, namespace="farts")
    else:
        ray.init(namespace="farts")
    result = do_launch(actor_count=args.actor_count)
    print(f"Got back {result} from launch")
