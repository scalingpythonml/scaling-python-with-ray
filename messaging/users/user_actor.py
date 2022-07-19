import logging
from messaging.internal_types import CombinedMessage
from messaging.utils import utils
from .models import Device, User
from messaging.proto.MessageDataPB_pb2 import EMAIL as EMAIL_PROTOCOL


# Seperate out the logic from the actor implementation so we can sub-class
# since you can not directly sub-class actors.


class UserActorBase():
    """
    Base client class for talking to the swarm.space APIs.
    Note: this actor is not async because django's ORM is not happy with
    async.
    """

    def __init__(self, idx: int, poolsize: int):
        self.idx = idx
        self.poolsize = poolsize
        self.satellite_pool = utils.LazyNamedPool("satellite", poolsize)
        self.mailclient_pool = utils.LazyNamedPool("mailclient", poolsize)
        logging.info(f"Starting user actor {idx}")

    def _fetch_user(self, msg: CombinedMessage) -> User:
        """
        Find the user associated with the message.
        """
        if (msg.from_device):
            device = Device.objects.get(serial_number=msg.msg_from)
            return device.user
        else:
            # TODO: handle e-mail
            username = msg.to
            try:
                return User.objects.get(username=username)
            except Exception as e:
                print(f"Failed to get user: {username}?")
                raise e

    def handle_message(self, input_msg: CombinedMessage):
        """
        Handle messages.
        """
        # TODO: Update the Sms item
        user = self._fetch_user(input_msg)
        # TODO: check subscriptions.
        # TODO: rename these functions to be more english-ish.
        # if user.customer_subscription is None:
        #     # Ignore users without an active subscription
        #     return
        # TODO - handle blocked numbers
        # blocked_numbers = BlockedNumber.object.get(user=user)
        # TODO - handle quota
        # Later TODO: handle more than e-mail
        if (input_msg.from_device):
            msg = {
                "data": input_msg.text,
                "msg_from": f"{user.username}@spacebeaver.com",
                "msg_to": input_msg.to
            }
            self.mailclient_pool.get_pool().submit(
                lambda actor, msg: actor.send_msg(**msg),
                msg)
        else:
            msg = {
                "protocol": EMAIL_PROTOCOL,
                "msg_from": input_msg.msg_from,
                "msg_to": user.device.serial_number,
                "data": input_msg.text
            }
            self.satellite_pool.get_pool().submit(
                lambda actor, msg: actor.send_message(**msg),
                msg)
