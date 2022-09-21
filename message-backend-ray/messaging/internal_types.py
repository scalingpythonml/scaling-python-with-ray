from typing import Union
from dataclasses import dataclass


@dataclass(frozen=True)
class CombinedMessage:
    text: str
    to: Union[str, int]
    msg_from: Union[str, int]
    protocol: int
    from_device: bool
