import base64
import unittest
import ray
from ..utils import test_utils
from . import mailserver_actor


class Envelop:
    def __init__(self):
        self.subject = ''
        self.content = base64.b64encode(b'Test content')
        self.rcpt_tos = []
        self.mail_from = "random@sender.co"


@ray.remote
class MailServerActorForTesting(mailserver_actor.MailServerActorBase):
    def __init__(self, idx, poolsize, port, hostname):
        mailserver_actor.MailServerActorBase.__init__(self, idx, poolsize, port, hostname)
        self.user_pool = test_utils.FakeLazyNamedPool("user", 1)


class MailServerActorTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ray.init()

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_mail_server_actor_construct(self):
        mailserver_actor.MailServerActor.remote(0, 1, 7587, "localhost")

    def test_mail_server_actor_test_construct(self):
        MailServerActorForTesting.remote(0, 1, 7587, "localhost")

    def test_handle_RCPT_valid_address_domain(self):
        mail_server = MailServerActorForTesting.remote(0, 1, 7587, "localhost")
        envelop = Envelop()
        msg_refs = mail_server.handle_RCPT.remote(1, 1, envelop, "abc@spacebeaver.com", 1)
        self.assertEqual(ray.get(msg_refs), "250 OK")

    def test_handle_RCPT_invalid_address_domain(self):
        mail_server = MailServerActorForTesting.remote(0, 1, 7587, "localhost")
        envelop = Envelop()
        msg_ref = mail_server.handle_RCPT.remote('', '', envelop, "abc@hotmail.com", 1)
        self.assertEqual(ray.get(msg_ref), "550 not relaying to that domain")

    def test_handle_DATA_without_rcpts(self):
        mail_server = MailServerActorForTesting.remote(0, 1, 7587, "localhost")
        envelop = Envelop()
        msg_ref = mail_server.handle_DATA.remote('', '', envelop)
        self.assertEqual(ray.get(msg_ref), "250 Message accepted for delivery")

    def test_handle_DATA_with_rcpts(self):
        mail_server = MailServerActorForTesting.remote(0, 1, 7587, "localhost")
        envelop = Envelop()
        envelop.rcpt_tos.append('test@spacebeaver.com')
        msg_ref = mail_server.handle_DATA.remote('', '', envelop)
        self.assertEqual(ray.get(msg_ref), "250 Message accepted for delivery")
