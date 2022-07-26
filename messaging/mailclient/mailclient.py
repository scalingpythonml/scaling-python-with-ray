import ray
import asyncio
import aiosmtplib
from email.message import EmailMessage
import logging
from messaging.settings.settings import Settings


class MailClient(object):
    """
    Mail Client
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def send_message(self, *args, **kwargs):
        """
        Wrap send_msg to include settings.
        """
        return self.send_msg.remote(self, *args, **kwargs)

    @ray.remote(retry_exceptions=True)
    def send_msg(self, msg_from: str, msg_to: str, data: str):
        message = EmailMessage()
        message["From"] = msg_from
        message["To"] = msg_to
        message["Subject"] = "A satelite msg: f{data.take(10)}"
        message.set_content(data)
        logging.info(f"Sending {message}")
        # TODO: Switch to built-in smtp client.
        return asyncio.run(aiosmtplib.send(
            message,
            hostname=self.settings.mail_server,
            port=self.settings.mail_port,
            username=self.settings.mail_username,
            password=self.settings.mail_password))
