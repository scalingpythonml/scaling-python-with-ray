import asyncio
import ray
import logging
import base64
import requests
from . import settings
from .internal_types import CombinedMessage
from . import utils

# Seperate out the logic from the actor implementation so we can sub-class
# since you can not directly sub-class actors.


class SateliteClientBase():
    """
    Base client class for talking to the swarm.space APIs.
    """

    def __init__(self, idx, poolsize):
        self.idx = idx
        self.poolsize = poolsize
        # Make sure we get enough messages for pool magic but also not too many
        self._page_request_size = max(
            min(50, 10 * poolsize),
            poolsize)
        self.user_pool = utils.LazyNamedPool("user", poolsize)
        self.max_internal_retries = 100
        self.session = requests.Session()
        self.delay = 60
        self._loginHeaders = {
            'Content-Type': 'application/x-www-form-urlencoded'}
        self._loginParams = settings.swarm_login_params
        self._hdrs = {'Accept': 'application/json'}
        self._hiveBaseURL = settings.hiveBaseURL
        self._loginURL = self._hiveBaseURL + '/login'
        self._getMessageURL = self._hiveBaseURL + '/api/v1/messages'
        self._ackMessageURL = self._hiveBaseURL + '/api/v1/messages/rxack/{}'
        print(f"Starting actor {idx}")

    async def run(self):
        internal_retries = 0
        while True:
            try:
                self._login()
                while True:
                    await asyncio.sleep(self.delay)
                    await self.check_msgs()
            except Exception as e:
                print(f"Error {e}, retrying")
                internal_retries = internal_retries + 1
                if (internal_retries > self.max_internal_retries):
                    raise e

    def _login(self):
        res = self.session.post(
            self._loginURL,
            data=self._loginParams,
            headers=self._loginHeaders)
        if res.status_code != 200:
            raise Exception(f"Login failure, exiting actor {res}")

    async def check_msgs(self):
        # TODO: Add message type
        res = self.session.get(
            self.getMessageURL,
            headers=self.hdrs,
            params={'count': self._page_request_size, 'status': 0})
        messages = res.json()
        for item in messages:
            # Is this a message we are responsible for
            if int(item["messageId"]) % self.poolsize == self.idx:
                try:
                    await self._process_mesage(item)
                except Exception as e:
                    logging.error(f"Error {e} processing {item}")
                self.session.post(
                    self._ackMessageURL.format(item['packetId']),
                    headers=self.hdrs)

    async def _process_message(self, item):
        raw_msg_data = item["data"]
        # temp hack, fix once we add the PB
        messagedata = MessageDataPB()  # noqa
        messagedata.ParseFromString(base64.b64decode(raw_msg_data))
        for message in messagedata.message:
            cm = CombinedMessage(
                text=message.text, to=message.to, protocol=message.protocol,
                deviceid=item["deviceId"]
            )
            # TODO: Update the count and check user
            self.user_pool.get_pool().submit(
                lambda actor,
                msg: actor.send_msg, cm)


@ray.remote(max_restarts=-1, lifetime="detached")
class SateliteClient(SateliteClientBase):
    """
    Connects to swarm.space API.
    """

    def __init__(self, idx, poolsize):
        SateliteClientBase.__init__(idx, poolsize)
