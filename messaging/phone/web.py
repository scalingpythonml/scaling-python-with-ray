from typing import List
from messaging.utils import utils
from pydantic import BaseModel, Field
from fastapi import FastAPI
from ray import serve
from messaging.settings.settings import Settings
from messaging.proto.MessageDataPB_pb2 import SMS as SMS_PROTOCOL
from messaging.internal_types import CombinedMessage
from typing import Optional


# 1: Define a FastAPI app and wrap it in a deployment with a route handler.
app = FastAPI()


# See https://dev.bandwidth.com/docs/messaging/webhooks/
class BandwidthMessage(BaseModel):
    time: str
    owner: str
    direction: str
    to: str
    message_from: str = Field(None, alias='from')
    text: str
    applicationId: str
    media: List[str]
    segmentCount: int


class InboundMessageParams(BaseModel):
    time: str
    description: str
    to: str
    message: BandwidthMessage
    msg_type: Optional[str] = Field(None, alias="type")


# See https://github.com/Bandwidth-Samples/messaging-send-receive-sms-python/blob/main/main.py
class CreateBody(BaseModel):
    to: str
    text: str


@serve.deployment(num_replicas=3, route_prefix="/")
@serve.ingress(app)
class PhoneWeb:
    def __init__(self, settings: Settings, poolsize: int):
        self.settings = settings
        self.poolsize = poolsize
        self.user_pool = utils.LazyNamedPool("user", poolsize)

    # FastAPI will automatically parse the HTTP request for us.
    @app.get("/callbacks/inbound/messaging")
    async def inbound_message(self, messages: List[InboundMessageParams]) -> int:
        for message_params in messages:
            message = message_params.message
            internal_message = CombinedMessage(
                text=message.text, to=message.to, protocol=SMS_PROTOCOL,
                msg_from=message.message_from, from_device=False
            )
            self.user_pool.get_pool().submit(
                lambda actor, msg: actor.handle_message.remote(msg), internal_message)
        return 200

    @app.post('/callbacks/outbound/messaging/status')
    async def handle_outbound_status(self, status_body_array: List[dict]) -> int:
        status_body = status_body_array[0]
        if status_body['type'] == "message-sending":
            print("message-sending type is only for MMS")
        elif status_body['type'] == "message-delivered":
            print("your message has been handed off to the Bandwidth's MMSC network")
        elif status_body['type'] == "message-failed":
            print("Message delivery failed")
        else:
            print("Message type does not match endpoint.")

        return 200
