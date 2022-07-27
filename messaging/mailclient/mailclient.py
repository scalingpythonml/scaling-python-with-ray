import ray
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        message = MIMEMultipart("alternative")
        message["From"] = msg_from
        message["To"] = msg_to
        message["Subject"] = f"A satelite msg: f{data[0:20]}"
        part1 = MIMEText(data, "plain")
        # Possible later: HTML
        message.attach(part1)

        with SMTP(self.settings.mail_server, port=self.settings.mail_port) as smtp:
            if self.settings.mail_username is not None:
                smtp.login(self.settings.mail_username,
                           self.settings.mail_password)
            logging.info(f"Sending message {message}")
            r = smtp.sendmail(
                msg=str(message),
                from_addr=msg_from,
                to_addrs=msg_to)
            return r
