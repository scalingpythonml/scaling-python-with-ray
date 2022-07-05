import asyncio
import aiosmtplib
from email.message import EmailMessage
import ray
import logging

class ClientActorBase():
    """
    Base mail client actor class
    """

    def __init__(self, idx: int, poolsize: int):
        self.idx = idx
        self.poolsize = poolsize
        
        

    async def send_msg(self, from: str, to: str, data: str):
        message = EmailMessage()
        message["From"] = from
        message["To"] = to
        message["Subject"] = "A satelite msg: f{data.take(10)}"
        message.set_content(data)
        await aiosmtplib.send(
            message,
            hostname=settings.mail_server,
            username=settings.mail_username,
            password=settings.mail_password)
