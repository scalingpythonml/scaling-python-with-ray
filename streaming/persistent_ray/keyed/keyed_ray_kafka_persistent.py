import ray
import json

@ray.remote
class KafkaProducer:
    def __init__(self, server: str = 'localhost:9092', topic: str = 'heatercontrol'):
        from confluent_kafka import Producer
        conf = {'bootstrap.servers': server}
        self.producer = Producer(**conf)
        self.topic = topic

    def produce(self, data: dict, key: str):

        def delivery_callback(err, msg):
            if err:
                print('Message failed delivery: ', err)
            else:
                print('Message delivered to topic ', msg.topic(), ' partition ', msg.partition(), ' offset', msg.offset())

        self.producer.produce(topic=self.topic, value=json.dumps(data).encode('UTF8'), key=key.encode('UTF8'), callback=delivery_callback)
        self.producer.poll(0)

    def destroy(self):
        self.producer.flush(30)

class TemperatureController:
    def __init__(self, producer: KafkaProducer, id: str):
        self.currentSetting = None
        self.previousCommand = -1
        self.id = id
        self.producer = producer

    # Process new message
    def process_new_message(self, message: dict):
        if 'measurement' in message:    # measurement request
            self.process_sensordata(message)
        else:                           # temp set request
            self.set_temperature(message)

    # set new temperature
    def set_temperature(self, setting: dict):
        desired = setting['temperature']
        updelta = setting['up_delta']
        downdelta = setting['down_delta']
        print('Controller ', self.id, ' new temperature setting ', desired, ' up delta ', updelta, ' down delta ', downdelta)
        self.currentSetting = desired
        self.upDelta = updelta
        self.downDelta = downdelta

    # Process new measurements
    def process_sensordata(self, sensor: dict):
        if self.currentSetting is not None:           # desired temperature is set, otherwise ignore
            # calculate desired action
            measurement = sensor['measurement']
            action = -1
            if measurement > (self.currentSetting + self.upDelta):
                action = 1
            if measurement < (self.currentSetting - self.downDelta):
                action = 0
            if action >= 0 and self.previousCommand != action:  # new action
                self.previousCommand = action
                # publish new action to kafka
                self.producer.produce.remote(data={'control': action}, key=self.id)

class TemperatureControllerManager:
    def __init__(self, producer: KafkaProducer):
        self.controllers = {}
        self.producer = producer

    def process_controller_message(self, request: dict, key: str):
        if not key in self.controllers:   # create a new controller
            print('Creating a new controller ', key)
            controller = TemperatureController(producer=self.producer, id=key)
            self.controllers[key] = controller
        self.controllers[key].process_new_message(request)

@ray.remote
class KafkaConsumer:
    def __init__(self, producer: KafkaProducer, group: str = 'ray', server: str = 'localhost:9092', topic: str = 'sensor', restart: str = 'earliest'):
        from confluent_kafka import Consumer
        import logging
        # Configuration
        consumer_conf = {'bootstrap.servers': server,   # bootstrap server
                 'group.id': group,                      # group ID
                 'session.timeout.ms': 6000,            # session tmout
                 'auto.offset.reset': restart}          # restart

        # Create Consumer instance
        self.consumer = Consumer(consumer_conf)
        self.topic = topic
        self.controller = TemperatureControllerManager(producer)

    def start(self):
        self.run = True
        def print_assignment(consumer, partitions):
            print('Assignment:', partitions)

        # Subscribe to topics
        self.consumer.subscribe([self.topic], on_assign = print_assignment)
        while self.run:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: ", msg.error())
                continue
            else:
                # Proper message
                print("New message: topic=", msg.topic(), ' partition=', msg.partition(),' offset=', msg.offset())
                value = json.loads(msg.value().decode('UTF8'))
                key = msg.key().decode('UTF8')
                print('key ', key, ' value ', value)
                self.controller.process_controller_message(value, key)

    def stop(self):
        self.run = False

    def destroy(self):
        self.consumer.close()

# Start Ray
ray.init()

# Start actors
producer = KafkaProducer.remote()
n_consumers = 5     # Number of consumers
consumers = [KafkaConsumer.remote(producer=producer) for _ in range(n_consumers)]

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