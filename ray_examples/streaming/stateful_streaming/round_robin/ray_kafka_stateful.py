import ray

from ray_examples.streaming.shared.kafka_actors import KafkaProducer
from ray_examples.streaming.shared.kafka_actors import BaseKafkaConsumer
from ray_examples.streaming.shared.controller import BaseTemperatureController

@ray.remote
class TemperatureController(BaseTemperatureController):
    def __init__(self, producer: KafkaProducer, id: str):
        super().__init__(id)
        self.producer = producer

    # Process new measurements
    def process_sensor_data(self, sensor: dict):
        if super().process_sensor_data(sensor):
            # publish new action to kafka
            self.producer.produce.remote({'control': self.previousCommand})

@ray.remote
class TemperatureControllerManager:
    def __init__(self, producer: KafkaProducer):
        self.controllers = {}
        self.producer = producer

    def process_controller_message(self, key: str, value: dict):
        controller_id = value['id']
        if not controller_id in self.controllers:   # create a new controller
            print(f'Creating a new controller {controller_id}')
            controller = TemperatureController.remote(producer=self.producer, id=controller_id)
            self.controllers[controller_id] = controller
        self.controllers[controller_id].process_new_message.remote(value)

@ray.remote
class KafkaConsumer(BaseKafkaConsumer):
    def __init__(self, callback, group: str = 'ray', server: str = 'localhost:9092',
                 topic: str = 'sensor', restart: str = 'earliest'):
        super().__init__(group=group, server = server, topic = topic, restart = restart)
        self.callback = callback

# Start Ray
ray.init()

# Start actors
producer = KafkaProducer.remote()
controller = TemperatureControllerManager.remote(producer)
n_consumers = 5     # Number of consumers
consumers = [KafkaConsumer.remote(controller.process_controller_message.remote) for _ in range(n_consumers)]
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
    ray.kill(controller)
