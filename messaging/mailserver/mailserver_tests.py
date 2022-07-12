import random
from smtplib import SMTP as Client
import unittest
from ..utils import test_utils
from ..proto.MessageDataPB_pb2 import EMAIL as EMAIL_PROTOCOL  # type: ignore

from . import mailserver_actor


class StandaloneMailServerActorTests(unittest.TestCase):
    port = 7779 + 100 * random.randint(0, 9)

    def setUp(self):
        self.port = self.port + 1
        self.actor = mailserver_actor.MailServerActorBase(
            idx=1, poolsize=1, port=self.port, hostname="0.0.0.0",
            label=None)
        self.actor.user_pool = test_utils.FakeLazyNamedPool("u", 1)
        self.pool = self.actor.user_pool.get_pool()

    def tearDown(self):
        self.actor.server.stop()
        self.server = None

    def test_constructor_makes_server(self):
        self.assertEquals(self.actor.server.hostname, "0.0.0.0")

    def test_extract_body_and_connect(self):
        client = Client("localhost", self.port)
        msg_text = "Hi Boop, this is farts."
        client.sendmail("farts@farts.com", "boop@spacebeaver.com",
                        msg_text)
        self.assertEquals(self.pool.submitted[0][1].text, msg_text)
        self.assertEquals(self.pool.submitted[0][1].protocol, EMAIL_PROTOCOL)
        self.assertEquals(self.pool.submitted[0][1].from_device, False)

    def test_smpt_emailmessage_send(self):
        from email.message import EmailMessage

        client = Client("localhost", self.port)
        msg = EmailMessage()
        msg_text = "Hi Boop, this is farts."
        msg_subject = "Maximum farts?"
        msg.set_content(msg_text)
        msg['From'] = "farts@farts.com"
        msg['To'] = "boop@spacebeaver.com"
        msg['Subject'] = msg_subject
        client.send_message(msg)
        self.assertEquals(self.pool.submitted[0][1].text, f"{msg_subject}\n{msg_text}")
        self.assertEquals(self.pool.submitted[0][1].protocol, EMAIL_PROTOCOL)
        self.assertEquals(self.pool.submitted[0][1].from_device, False)
