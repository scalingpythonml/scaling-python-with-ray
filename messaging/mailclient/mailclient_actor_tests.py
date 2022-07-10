# import unittest
# from unittest.mock import patch
# import ray

# from . import mailclient_actor

# @ray.remote
# @patch('aiosmtplib.send', return_value=1)
# class MailClientForTesting(mailclient_actor.MailClientActorBase):
#     pass

# class MailClientTestCases(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         ray.init()

#     @classmethod
#     def tearDownClass(cls):
#         ray.shutdown()

#     def test_send_msg(self):
#         mail_client = MailClientForTesting.remote()
#         mail_ref = mail_client.send_msg.remote(
#             "test@test.com", "receiver@receiver.com", "test msg"
#         )
#         self.assertEqual(ray.get(mail_ref), 1)
