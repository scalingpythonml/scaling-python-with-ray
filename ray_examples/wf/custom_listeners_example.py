from ray import workflow

class EventListener:
    def __init__(self):
        """Optional constructor. Only the constructor with now arguments will be
          called."""
        pass
 
    async def poll_for_event(self, *args, **kwargs) -> Event:
        """Should return only when the event is received."""
        raise NotImplementedError
 
    async def event_checkpointed(self, event: Event) -> None:
        """Optional. Called after an event has been checkpointed and a transaction can
          be safely committed."""
        pass
