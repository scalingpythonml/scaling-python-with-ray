import ray
import asyncio
import aiosmtplib
from email.message import EmailMessage
import logging
from messaging.settings import settings


class MailClient(object):
    """
    Mail Client
    """

    @ray.remote(retry_exceptions=True)
    def send_msg(self, msg_from: str, msg_to: str, data: str):
        message = EmailMessage()
        message["From"] = msg_from
        message["To"] = msg_to
        message["Subject"] = "A satelite msg: f{data.take(10)}"
        message.set_content(data)
        logging.info(f"Sending {message}")
        return asyncio.run(aiosmtplib.send(
            message,
            hostname=settings.mail_server,
            username=settings.mail_username,
            password=settings.mail_password))
