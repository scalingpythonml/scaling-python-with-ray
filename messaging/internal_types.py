from dataclasses import dataclass


@dataclass(frozen=True)
class CombinedMessage:
    text: str
    to: str
    protocol: int
    deviceid: int
