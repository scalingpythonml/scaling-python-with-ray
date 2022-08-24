from messaging.settings.settings import Settings
from messaging.internal_types import CombinedMessage
from bandwidth.messaging.models.message_request import MessageRequest


class OutboundPhoneBase():
    """
    Base client for talking to our outbound SMS provider.
    """

    def __init__(self,  settings: Settings, idx: int, poolsize: int):
        print(f"Running on {platform.machine()}")
        self.settings = settings
        self.idx = idx
        self.poolsize = poolsize
        self.bandwidth_client = BandwidthClient(
            messaging_basic_auth_user_name=settings.BW_USERNAME,
            messaging_basic_auth_password=settings.BW_PASSWORD
        )
        self.messaging_client = bandwidth_client.messaging_client.client
        self.settings = settings


    async def send_message(self, msg_from: str, msg_to: str, data: str):
        body = MessageRequest()
        body.application_id = self.settings.BW_MESSAGING_APPLICATION_ID
        body.to = [msg_to]
        body.mfrom = msg_from
        body.text = data
        messaging_client.create_message(account_id, body=body)


@ray.remote(max_restarts=-1)
class OutboundPhone(OutboundPhoneBase):
    """
    Sends outbound SMS messages.
    """
                                    
