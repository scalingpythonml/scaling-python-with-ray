import ray
from ray.util import ActorPool
from messaging.satellite.satellite import SatelliteClient
from messaging.mailserver.mailserver_actor import MailServerActor
from messaging.mailclient.mailclient_actor import MailClientActor


def make_satellite_actor(idx: int):
    return (SatelliteClient.options(name=f"satelite_{idx}")  # type: ignore
            .remote(idx, actor_count))


actor_count = 2
actor_idxs = list(range(0, actor_count))
satellite_actors = list(map(make_satellite_actor, actor_idxs))
# Since the satellite actors are polling, start them running.
for actor in satellite_actors:
    actor.run.remote()
satelite_pool = ActorPool(satellite_actors)
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
                name=f"mailserver_{idx}", placement_group=mailserver_pg, num_cpus=0.1)
            .remote(
                idx=idx,
                poolsize=actor_count,
                port=7420,
                hostname="spacebeaver.com",
                label="mail_ingress"))


mailserver_actors = list(map(make_mailserver_actor, actor_idxs))
mailserver_pool = ActorPool(mailserver_actors)


def make_mailclient_actor(idx: int):
    return (MailClientActor  # type: ignore
            .options(name=f"mailclient_{idx}")
            .remote())


mailclient_actors = list(map(make_mailclient_actor, actor_idxs))  # type: ignore
mailclient_pool = ActorPool(mailclient_actors)
# f = mailclient_pool.submit(
#     lambda actor, v: actor.send_msg.remote(*v),
#     ["timbit", "farts", "data"])
# print(mailclient_pool.get_next())
