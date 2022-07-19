import os
import ray
# This needs to be before importing the django models.
from .django_test import test_id
import unittest
from ..utils import test_utils  # noqa
from messaging.internal_types import CombinedMessage
from .models import Device, User, django_path
from ..proto.MessageDataPB_pb2 import EMAIL as EMAIL_PROTOCOL  # type: ignore
from . import user_actor


@ray.remote
class UserActorForTesting(user_actor.UserActorBase):
    def __init__(self, idx, poolsize):
        user_actor.UserActorBase.__init__(self, idx, poolsize)
        self.satellite_pool = test_utils.FakeLazyNamedPool("satellite", 5)
        self.mailclient_pool = test_utils.FakeLazyNamedPool("mailclient", 5)


class UserActorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=4, num_gpus=0)
        # Sketchy to use shell but otherwise django gets unhappy
        # Also kind of slow move.
        os.system(f"cd {django_path}; TEST_ID={test_id} python manage.py migrate")

    def setUp(self):
        d1 = Device.objects.create(serial_number=1234)
        d2 = Device.objects.create(serial_number=1235)
        self.user_with_device_and_subscription = User.objects.create(
            username="farts", email="fart22@fart.com")
        self.user_with_device = User.objects.create(username="mcgee")
        self.standalone_user = User.objects.create(username="went")
        d1.assign_to_user(self.user_with_device_and_subscription)
        d1.save()
        self.user_with_device_and_subscription.is_active = True
        # TODO: Make a test subscription (?)
        self.user_with_device_and_subscription.save()
        d2.assign_to_user(self.user_with_device)
        d2.save()

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_valid_user_inbound(self):
        test_text = "Farts mcgee went to the fart to fart fartly."
        to = "farts"
        msg_from = "butts"
        input_msg = CombinedMessage(
            text=test_text,
            to=to,
            msg_from=msg_from,
            protocol=EMAIL_PROTOCOL,
            from_device=False)
        actor = user_actor.UserActorBase(0, 1)
        actor.satellite_pool = test_utils.FakeLazyNamedPool("satellite", 5)
        actor.mailclient_pool = test_utils.FakeLazyNamedPool("mailclient", 5)
        actor.handle_message(input_msg)
        self.assertEquals(
            actor.satellite_pool.get_pool().submitted[0][1],
            {'msg_from': msg_from,
             'msg_to': '1234',
             'protocol': 1,
             'data': test_text})
