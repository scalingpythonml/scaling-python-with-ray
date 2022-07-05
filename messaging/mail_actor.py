import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as Server, syntax
from aiosmtpd.handlers import Sink
import aiosmtp
import ray
import logging

class CustomMailServer(Server):
    def __init__(handler, hostname: Option[str]):
        super().__init__(
            handler=handler,
            hostname=hostname,
            ident="SpaceBeaver GateWay (PCFLabsLLC)")
    

class ServerActorBase():
    """
    Base server mail actor class
    """

    def __init__(self, idx: int, poolsize: int, port: int, hostname: str, label: Option[str]):
        self.idx = idx
        self.poolsize = poolsize
        

    def apply_label(self):
        # See https://stackoverflow.com/questions/36147137/kubernetes-api-add-label-to-pod

    async def send_msg(self, 
        
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
         """
         Call back for RCPT. This only accept e-mail for us, no relaying.
         """
         if not address.endswith(f"@{self.hostname}"):
             return '550 not relaying to that domain'
         envelope.rcpt_tos.append(address)
         return '250 OK'

     async def handle_DATA(self, server, session, envelope):
         """
         Call back for 
         print('Message from %s' % envelope.mail_from)
         print('Message for %s' % envelope.rcpt_tos)
         print('Message data:\n')
         for ln in envelope.content.decode('utf8', errors='replace').splitlines():
             print(f'> {ln}'.strip())
         print()
         print('End of message')
         return '250 Message accepted for delivery'

        
