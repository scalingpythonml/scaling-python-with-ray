# We need this before the imports because django.
import os
import uuid
os.environ["DJANGO_CONFIGURATION"] = "UnitTest"
os.environ["__ENV__"] = "UnitTest"
os.environ["SECRET_KEY"] = "d7b24a10f65b4cae8549d79991ebaf2b"
os.environ["STRIPE_TEST_SECRET_KEY"] = "sk_test_very_secret"
os.environ["DJSTRIPE_WEBHOOK_SECRET"] = "very_secret2"


import unittest
from ..utils import test_utils
from messaging.internal_types import CombinedMessage
from .models import Device, User, django_path
from ..proto.MessageDataPB_pb2 import EMAIL as EMAIL_PROTOCOL  # type: ignore

class UserActorTests(unittest.TestCase):
    def setUp(self):
        # Sketchy to use shell but otherwise django gets unhappy
        # Also kind of slow move to before/after all
        os.environ["TEST_ID"] = str(uuid.uuid1())
        os.system(f"cd {django_path}; python manage.py migrate")

        d1 = Device.objects.create(serial_number=1234)
        d2 = Device.objects.create(serial_number=1235)
        self.user_with_device_and_subscription = User.objects.create(
            username="farts", customer__email="fart22@fart.com")
        self.user_with_device = User.objects.create(username="mcgee")
        self.standalone_user = User.objects.create(username="went")
        d1.assign_to_user(self.user_with_device_and_subscription)
        d1.save()
        Subscription.objects.create(
            customer__email="fart22@fart.com",
            status="active")
        d2.assign_to_user(self.user_with_device)
        d2.save()
        self.actor = UserActorBase(0, 1)
        self.actor.satellite_pool = test_utils.FakeLazyNamedPool("satellite")
        self.actor.mailclient_pool = test_utils.FakeLazyNamedPool("mailclient")

    def test_valid_user_inbound(self):
        input_msg = CombinedMessage(
            text="Farts mcgee went to the fart to fart fartly.",
            to="farts",
            msg_from="butts",
            protocol=EMAIL_PROTOCOL,
            from_device=False)
        self.actor.handle_message(input_msg)
        assertEquals(self.actor.satellite_pool.submitted, [])
