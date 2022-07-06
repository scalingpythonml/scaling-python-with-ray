import asyncio
import ray
import logging
import base64
import requests
from messaging.settings import settings
from messaging.internal_types import CombinedMessage
from messaging.utils import utils
from google.protobuf import text_format
from messaging.proto.MessageDataPB_pb2 import MessageDataPB  # type: ignore
from typing import AsyncIterator, List


# Seperate out the logic from the actor implementation so we can sub-class
# since you can not directly sub-class actors.


class SatelliteClientBase():
    """
    Base client class for talking to the swarm.space APIs.
    """

    def __init__(self, idx: int, poolsize: int):
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
        logging.info(f"Starting actor {idx}")

    async def run(self):
        internal_retries = 0
        while True:
            try:
                self._login()
                while True:
                    await asyncio.sleep(self.delay)
                    await self.check_msgs()
            except Exception as e:
                logging.info(f"Error {e}, retrying")
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

    async def _decode_message(self, item: dict) -> AsyncIterator[CombinedMessage]:
        """
        Decode a message. Note: result is not serializable.
        """
        raw_msg_data = item["data"]
        logging.info(f"msg: {raw_msg_data}")
        # temp hack, fix once we add the PB
        messagedata = MessageDataPB()  # noqa
        bin_data = base64.b64decode(raw_msg_data)
        # Note: this really does no validation, so if it gets a message instead
        # of MessageDataPb it just gives back nothing
        messagedata.ParseFromString(bin_data)
        logging.info(f"Formatted: {text_format.MessageToString(messagedata)}")
        if (len(messagedata.message) < 1):
            logging.warn(f"Received {raw_msg_data} with no messages?")
        for message in messagedata.message:
            yield CombinedMessage(
                text=message.text, to=message.to, protocol=message.protocol,
                msg_from=item["deviceId"], from_device=True
            )

    async def _ser_decode_message(self, item: dict) -> List[CombinedMessage]:
        """
        Decode a message. Serializeable but blocking
        """
        gen = self._decode_message(item)
        # See PEP-0530
        return [i async for i in gen]

    async def _process_message(self, item: dict):
        messages = self._decode_message(item)
        # TODO: Update the count and check user
        async for message in messages:
            self.user_pool.get_pool().submit(
                lambda actor, msg: actor.handle_message,
                message)


@ray.remote(max_restarts=-1)
class SatelliteClient(SatelliteClientBase):
    """
    Connects to swarm.space API.
    """
