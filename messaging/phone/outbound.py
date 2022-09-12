from messaging.settings.settings import Settings
import ray
import platform
from twilio.rest import Client


class OutboundPhoneBase():
    """
    Base client for talking to our outbound SMS provider.
    """

    def __init__(self, settings: Settings, idx: int, poolsize: int):
        print(f"Running on OutboundPhoneBase {idx} on type {platform.machine()}")
        self.settings = settings
        self.idx = idx
        self.poolsize = poolsize
        self.twilio_client = Client(
            settings.TW_USERNAME,
            settings.TW_PASSWORD
        )
        self.settings = settings

    async def send_message(self, msg_from: str, msg_to: str, data: str):
        self.twilio_client.messages.create(
            to=msg_to,
            from_=msg_from,
            body=data)


@ray.remote(max_restarts=-1)
class OutboundPhone(OutboundPhoneBase):
    """
    Sends outbound SMS messages.
    """
