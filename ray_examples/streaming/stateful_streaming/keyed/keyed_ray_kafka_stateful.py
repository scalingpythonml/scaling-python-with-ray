import ray

from ray_examples.streaming.shared.kafka_actors import KafkaProducer
from ray_examples.streaming.shared.kafka_actors import BaseKafkaConsumer
from ray_examples.streaming.shared.controller import BaseTemperatureController

class TemperatureController(BaseTemperatureController):
    def __init__(self, producer: KafkaProducer, id: str):
        super().__init__(id)
        self.producer = producer

    # Process new measurements
    def process_sensordata(self, sensor: dict):
        if super().process_sensordata(sensor):
            # publish new action to kafka
            self.producer.produce.remote(data={'control': self.previousCommand}, key=self.id)

class TemperatureControllerManager:
    def __init__(self, producer: KafkaProducer):
        self.controllers = {}
        self.producer = producer

    def process_controller_message(self, key: str, request: dict):
        if not key in self.controllers:   # create a new controller
            print(f'Creating a new controller {key}')
            controller = TemperatureController(producer=self.producer, id=key)
            self.controllers[key] = controller
        self.controllers[key].process_new_message(request)

@ray.remote
class KafkaConsumer(BaseKafkaConsumer):
    def __init__(self, producer: KafkaProducer, group: str = 'ray', server: str = 'localhost:9092',
                 topic: str = 'sensor', restart: str = 'earliest'):
        super().__init__(group=group, server = server, topic = topic, restart = restart)
        self.callback = TemperatureControllerManager(producer).process_controller_message

# Start Ray
ray.init()

# Start actors
producer = KafkaProducer.remote()
n_consumers = 5     # Number of consumers
consumers = [KafkaConsumer.remote(producer) for _ in range(n_consumers)]

refs = [c.start.remote() for c in consumers]

try:
    ray.get(refs)

# end gracefully
except KeyboardInterrupt:
    for c in consumers:
        c.stop.remote()
finally:
    for c in consumers:
        c.destroy.remote()
    producer.destroy.remote()
    ray.kill(producer)