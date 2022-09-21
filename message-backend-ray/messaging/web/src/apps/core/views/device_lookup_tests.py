from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from apps.core.models import Device


User = get_user_model()
UserStub = namedtuple("User", "username full_name email password")
test_user_data = UserStub(
    "farts",
    "test-fullname",
    "somewhere@test.com",
    "&Aqa&5y!8wMpWGUC8gJBWqpxjE8p8nT7XDB2xwZA4$KEb9Nd2&&kv42Y*!Vg4kHE8fPw5k2PwBSD$y*bqzEmXdH8fe#F4#BdY5x",
)
test_device_id = "070065082084083"  # FARTS


class DeviceLookupTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username=test_user_data.username,
            full_name=test_user_data.full_name,
            email=test_user_data.email,
        )
        user.is_active = True
        user.set_password(test_user_data.password)
        user.save()
        device = Device(serial_number=test_device_id)
        device.assign_to_user(user)
        device.save()

    def test_lookup_good_device(self):
        c = Client()
        response = c.get("/device_lookup", {"device_id": test_device_id})
        self.assertEqual(response.status_code, 200)

    def test_lookup_bad_device(self):
        c = Client()
        response = c.get("/device_lookup", {"device_id": "farts"})
        self.assertEqual(response.status_code, 402)

    def test_lookup_no_device(self):
        c = Client()
        response = c.get("/device_lookup")
        self.assertEqual(response.status_code, 400)
