import asyncio
import unittest
import ray
import os
import json
import base64
from ..utils import test_utils
from ..proto.MessageDataPB_pb2 import MessageDataPB, EMAIL as EMAIL_PROTOCOL  # type: ignore
from messaging.settings.settings import Settings

os.environ["hivebaseurl"] = "http://www.farts.com"

from . import satellite  # noqa: E402

test_data = MessageDataPB()
test_data.version = 0
test_data.from_device = True
test_msg = test_data.message.add()
test_msg.text = "Test"
test_msg.to = "timbit@pigscanfly.ca"
test_msg.protocol = EMAIL_PROTOCOL
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


class StandaloneSatelliteTests(unittest.TestCase):
    def test_login_fails(self):
        s = satellite.SatelliteClientBase(Settings(), 0, 1)
        self.assertRaises(Exception, s._login)

    async def decode_msg(self):
        s = satellite.SatelliteClientBase(Settings(), 0, 1)
        messages = s._decode_message(raw_msg_item)
        async for message in messages:
            print(f"Message {message}")

    def test_decode_msg(self):
        asyncio.run(self.decode_msg())


@ray.remote
class SatelliteClientForTesting(satellite.SatelliteClientBase):
    def __init__(self, idx, poolsize):
        satellite.SatelliteClientBase.__init__(self, Settings(), idx, poolsize)
        self.user_pool = test_utils.FakeLazyNamedPool("user", 1)


class RaySatelliteTests(unittest.TestCase):
    """
    Test for the satellite magic.
    """
    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=4, num_gpus=0)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_satellite_client_construct(self):
        mysatellite = satellite.SatelliteClient.remote(Settings(), 0, 1)  # noqa: F841

    def test_satellite_client_test_construct(self):
        mysatellite = SatelliteClientForTesting.remote(0, 1)  # noqa: F841

    def test_satellite_client_test_message_parse(self):
        mysatellite = SatelliteClientForTesting.remote(0, 1)
        msgs_ref = mysatellite._ser_decode_message.remote(raw_msg_item)
        msgs = ray.get(msgs_ref)
        self.assertEquals(len(msgs), 1)
        self.assertEquals(msgs[0].msg_from, 1)
