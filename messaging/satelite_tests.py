import asyncio
import unittest
import ray
import os
import json
import base64
from . import test_utils
from .proto.MessageDataPB_pb2 import MessageDataPB, Protocol  # type: ignore

os.environ["hivebaseurl"] = "http://www.farts.com"

from . import satelite  # noqa: E402

test_data = MessageDataPB()
test_data.version = 0
test_data.from_device = True
test_msg = test_data.message.add()
test_msg.text = "Test"
test_msg.to = "timbit@pigscanfly.ca"
test_msg.protocol = Protocol.EMAIL
test_data_encoded = base64.b64encode(test_data.SerializeToString())
test_item = """{
"packetId": 0,
"deviceType": 0,
"deviceId": 1,
"deviceName": "string",
"dataType": 0,
"userApplicationId": 0,
"len": 0,
"data": "{data}",
"ackPacketId": 0,
"status": 0,
"hiveRxTime": "2021-12-26T07:44:26.374Z"
}""".replace("{data}", test_data_encoded.decode("ascii"))
raw_msg_item = json.loads(test_item)


class StandaloneSateliteTests(unittest.TestCase):
    def test_login_fails(self):
        s = satelite.SateliteClientBase(0, 1)
        self.assertRaises(Exception, s._login)

    async def decode_msg(self):
        s = satelite.SateliteClientBase(0, 1)
        messages = s._decode_message(raw_msg_item)
        async for message in messages:
            print(f"Message {message}")

    def test_decode_msg(self):
        asyncio.get_event_loop().run_until_complete(self.decode_msg())


@ray.remote
class SateliteClientForTesting(satelite.SateliteClientBase):
    def __init__(self, idx, poolsize):
        satelite.SateliteClientBase.__init__(self, idx, poolsize)
        self.user_pool = test_utils.FakeLazyNamedPool("user", 1)


class RaySateliteTests(unittest.TestCase):
    """
    Test for the satelite magic.
    """
    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=4, num_gpus=0)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_satelite_client_construct(self):
        mysatelite = satelite.SateliteClient.remote(0, 1)  # noqa: F841

    def test_satelite_client_test_construct(self):
        mysatelite = SateliteClientForTesting.remote(0, 1)  # noqa: F841

    def test_satelite_client_test_message_parse(self):
        mysatelite = SateliteClientForTesting.remote(0, 1)
        msgs_ref = mysatelite._ser_decode_message.remote(raw_msg_item)
        msgs = ray.get(msgs_ref)
        self.assertEquals(len(msgs), 1)
        self.assertEquals(msgs[0].msg_from, 1)
