import requests
from pydantic import BaseModel
from fastapi import FastAPI, Field, Query
from ray import serve
from messaging.settings.settings import Settings
from messaging.proto.MessageDataPB_pb2 import Protocol  # type: ignore
from messaging.internal_types import CombinedMessage

# 1: Define a FastAPI app and wrap it in a deployment with a route handler.
app = FastAPI()

# See https://dev.bandwidth.com/docs/messaging/webhooks/
class InboundMessageParams(BaseModel):
    time: str,
    description: str,
    to: str,
    message: BandwidthMessage,
    msg_type: Optional[str] = Field(None, alias="type")

class BandwidthMessage(BaseModel):
    time: str
    owner: str
    direction: str
    to: str
    message_from: str = Field(None, alias='from')
    text: str
    applicationId: str
    media: array[str]
    segmentCount: int

# See https://github.com/Bandwidth-Samples/messaging-send-receive-sms-python/blob/main/main.py
class CreateBody(BaseModel):
    to: str
    text: str

    

@serve.deployment(num_replicas=3, route_prefix="/")
@serve.ingress(app)
class PhoneWeb:
    def __init__(self, settings: Settings, idx: int, poolsize: int):
        self.settings = settings
        self.idx = idx
        self.poolsize = poolsize
        self.user_pool = utils.LazyNamedPool("user", poolsize)

    # FastAPI will automatically parse the HTTP request for us.
    @app.get("/callbacks/inbound/messaging")
    async def inbound_message(self, messages: array[InboundMessageParams] ) -> str:
        for message in messages:
            internal_message = CombinedMessage(
                text=message.text, to=message.to, protocol=Protocol.SMS,
                msg_from=message.message_from, from_device=False
            )
            user_pool.get_pool().submit(
                lambda actor, msg: actor.handle_message.remote(msg), internal_message)
        return True

    @app.post('/callbacks/outbound/messaging/status')
    async def handle_outbound_status(request: Request):
        status_body_array = await request.json()
        status_body = status_body_array[0]
        if status_body['type'] == "message-sending":
            print("message-sending type is only for MMS")
        elif status_body['type'] == "message-delivered":
            print("your message has been handed off to the Bandwidth's MMSC network, but has not been confirmed at the downstream carrier")
        elif status_body['type'] == "message-failed":
            print("For MMS and Group Messages, you will only receive this callback if you have enabled delivery receipts on MMS.")
        else:
            print("Message type does not match endpoint. This endpoint is used for message status callbacks only.")

        return 200
