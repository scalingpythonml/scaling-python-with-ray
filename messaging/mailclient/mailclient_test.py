import unittest
import os
import asyncio
from aiosmtpd.controller import Controller
import ray
from . import MailClient
from messaging.settings.settings import Settings


class MailClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=8, num_gpus=0)

    def setUp(self):
        port = 7777
        hostname = "localhost"
        self.msgs = []
        self.server = Controller(
            handler=self,
            hostname=hostname,
            ident="SpaceBeaver (PCFLabsLLC)",
            port=port)
        self.server.start()
        os.environ["mail_server"] = hostname
        os.environ["mail_port"] = f"{port}"
        self.client = MailClient(Settings())

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def tearDown(self):
        self.server.stop()

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        self.msgs += envelope

    async def bloop(self):
        """
        Yield to allow mail server to run.
        """
        await asyncio.sleep(10)

    def test_mailclient(self):
        self.client.send_message(
            msg_from="farty@fart.com",
            msg_to="sirfarts@fart.com",
            data="Please send TP, I went to taco-bell.")
        asyncio.run(self.bloop())
        self.assertEquals(self.msgs, [])
