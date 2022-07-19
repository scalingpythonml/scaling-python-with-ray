from email import message_from_bytes, policy
from aiosmtpd.controller import Controller
import ray
import logging
import requests
from typing import Optional
from messaging.utils.utils import LazyNamedPool
import os
from messaging.internal_types import CombinedMessage
from messaging.proto.MessageDataPB_pb2 import Protocol  # type: ignore
from email.utils import parseaddr


class MailServerActorBase():
    """
    Base server mail actor class
    """

    def __init__(self, idx: int, poolsize: int, port: int, hostname: str,
                 label: Optional[str] = None):
        self.idx = idx
        self.poolsize = poolsize
        self.user_pool = LazyNamedPool("user", poolsize)
        self.domain = "spacebeaver.com"
        self.server = Controller(
            handler=self,
            hostname=hostname,
            ident="SpaceBeaver (PCFLabsLLC)",
            port=port)
        self.server.start()
        self.label = label
        if label is not None:
            self.apply_label()

    def apply_label(self):
        # See https://stackoverflow.com/questions/36147137/kubernetes-api-add-label-to-pod
        label = self.label
        patch_json = (
            "[{" +
            f""" "op": "add", "path": "/metadata/labels/{label}", "value": "present" """ +
            "}]")
        kube_host = os.getenv("KUBERNETES_SERVICE_HOST")
        kube_port = os.getenv("KUBERNETES_PORT_443_TCP_PORT", "443")
        pod_namespace = os.getenv("POD_NAMESPACE")
        pod_name = os.getenv("POD_NAME")
        url = f"https://{kube_host}:{kube_port}/api/v1/namespace/{pod_namespace}/pods/{pod_name}"
        headers = {"Content-Type": "application/json-patch+json"}
        result = requests.post(url, data=patch_json, headers=headers)
        logging.info(f"Got back {result} updating header.")

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        """
        Call back for RCPT. This only accept e-mail for us, no relaying.
        """
        logging.info(f"RCPT to with {address} received.")
        if not address.endswith(f"@{self.domain}"):
            return '550 not relaying to that domain'
        # Do we really want to support multiple e-mails? idk.
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        """
        Call back for the message data.
        """
        logging.info(f"Received message {envelope}")
        print('Message for %s' % envelope.rcpt_tos)
        parsed_email = message_from_bytes(envelope.content, policy=policy.SMTPUTF8)
        text = ""
        if "subject" in parsed_email:
            subject = parsed_email["subject"]
            text = f"{subject}\n"
        body = None
        # You would think "get_body" would give us the body but... maybe not? ugh
        try:
            body = parsed_email.get_body(preferencelist=('plain', 'html',)).get_content()
        except Exception:
            if parsed_email.is_multipart():
                for part in parsed_email.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))

                    # skip any text/plain (txt) attachments
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)  # decode
                        break
                    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
            else:
                body = parsed_email.get_payload(decode=True)
        text = f"{text}{body}"
        text = text.replace("\r\n", "\n").rstrip("\n")
        for rcpt in envelope.rcpt_tos:
            message = CombinedMessage(
                text=text,
                to=parseaddr(rcpt)[1].split('@')[0],
                msg_from=envelope.mail_from,
                from_device=False,
                protocol=Protocol.EMAIL)
            self.user_pool.get_pool().submit(
                lambda actor, message: actor.handle_message(message),
                message)
        return '250 Message accepted for delivery'


@ray.remote
class MailServerActor(MailServerActorBase):
    """
    Mail server actor class
    """
