import ray
from pprint import pprint
import base64
import json
import requests
from settings import *
from internal_types import *
from utils import *


ray.init()

@ray.remote(max_restarts=-1, lifetime="detached")
class SateliteClient():
    """
    Connects to swam.space API.
    """
    loginHeaders = {'Content-Type': 'application/x-www-form-urlencoded'}
    hdrs = {'Accept': 'application/json'}
    hiveBaseURL = 'https://bumblebee.hive.swarm.space/hive'
    loginURL = hiveBaseURL + '/login'
    getMessageURL = hiveBaseURL + '/api/v1/messages'
    ackMessageURL = hiveBaseURL + '/api/v1/messages/rxack/{}'

    def __init__(self, idx, poolsize):
        self.idx = idx
        self.poolsize = poolsize
        self.user_pool = LazyNamedPool("user", poolsize)
        self.max_internal_retries = 100
        self.session = requests.Session()
        print(f"Starting actor {idx}")
        asyncio.run(self.dowork())
        print("Done!")

    async def workloop(self):
        internal_retries = 0
        while True:
            try:
                self._login()
                while True:
                    await asyncio.sleep(1)
                    await self.check_msgs(s)
            except Exception as e:
                print(f"Error {e}, retrying")
                internal_retries = internal_retries + 1
                if (internal_retries > self.max_internal_retries):
                    raise e

    def _login(self):
        res = self.session.post(loginURL, data=loginParams, headers=loginHeaders)
        if res.status_code != 200:
            print(f"Login failure, exiting actor {res}")
            exit(1)
            
    async def check_msgs(self):
        res = self.session.get(getMessageURL, headers=hdrs, params={'count': 10, 'status': 0})
        messages = res.json()
        for item in messages:
            # Is this a message we are responsible for
            if int(item["messageId"]) % poolsize == idx:
                await self._process_mesage(item)
                self.session.post(ackMessageURL.format(item['packetId']), headers=hdrs)

    async def _process_message(item):
        raw_msg_data = item["data"]
        messagedata = MessageDataPB()
        messagedata.ParseFromString(base64.b64decode(raw_msg_data))
        for message in messagedata.message:
            cm = CombinedMessage(
                text=message.text, to=message.to, protocol=message.protocol,
                deviceid=item["deviceId"]
            )
            # TODO: Update the count and check user
            self.user_pool.get_pool().submit(lambda smtp_actor, msg: smtp_actor.send_msg, cm)
        

def make_actor(idx):
    return (SateliteClient.options(name=f"satelite_{idx}")
            .remote(idx, actor_count))
actor_count = 10
actor_idx = list(range(0, actor_count))
actors = list(map(make_actor, actor_idx))
satelite_pool = ActorPool(actors)
