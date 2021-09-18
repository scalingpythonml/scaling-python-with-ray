import ray
import json
from time import sleep
from random import seed
from random import randint
from streaming.shared.kafka_support import setup_topics

@ray.remote
class KafkaProducer:
    def __init__(self, server: str = 'localhost:9092'):
        from confluent_kafka import Producer
        conf = {'bootstrap.servers': server}
        self.producer = Producer(**conf)

    def produce(self, data: dict, key: str = None, topic: str = 'test'):

        def delivery_callback(err, msg):
            if err:
                print(f'Message failed delivery: {err}')
            else:
                print(f'Message delivered to topic {msg.topic()} partition {msg.partition()} offset {msg.offset()}')

        binary_key = None
        if key is not None:
            binary_key = key.encode('UTF8')
        self.producer.produce(topic=topic, value=json.dumps(data).encode('UTF8'), key=binary_key, callback=delivery_callback)
        self.producer.poll(0)

    def destroy(self):
        self.producer.flush(30)

@ray.remote
class KafkaConsumer:
    def __init__(self, callback, group: str = 'ray', server: str = 'localhost:9092', topic: str = 'test', restart: str = 'latest'):
        from confluent_kafka import Consumer
        from uuid import uuid4
        # Configuration
        consumer_conf = {'bootstrap.servers': server,   # bootstrap server
                 'group.id': group,                      # group ID
                 'session.timeout.ms': 6000,            # session tmout
                 'auto.offset.reset': restart}          # restart

        # Create Consumer instance
        self.consumer = Consumer(consumer_conf)
        self.topic = topic
        self.callback = callback
        self.id = str(uuid4())

    def start(self):
        self.run = True
        def print_assignment(consumer, partitions):
            print(f'Consumer: {self.id}')
            print(f'Assignment: {partitions}')

        # Subscribe to topics
        self.consumer.subscribe([self.topic], on_assign = print_assignment)
        while self.run:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f'Consumer error: {msg.error()}')
                continue
            else:
                # Proper message
                self.callback(self.id, msg)

    def stop(self):
        self.run = False

    def destroy(self):
        self.consumer.close()

# Simple callback function to print topics
def print_message(consumer_id: str, msg):
    print(f"Consumer {consumer_id} new message: topic={msg.topic()}  partition= {msg.partition()}  "
          f"offset={msg.offset()} key={msg.key().decode('UTF8')}")
    print(json.loads(msg.value().decode('UTF8')))

# Setup topics
setup_topics(topics=['test'])

# Setup rundom number generator
seed(1)

# Start Ray
ray.init()

# Start consumers and producers
n_consumers = 5     # Number of consumers
consumers = [KafkaConsumer.remote(print_message) for _ in range(n_consumers)]
producer = KafkaProducer.remote()
refs = [c.start.remote() for c in consumers]

# publish messages
user_name = 'john'
user_favorite_color = 'blue'

try:
    while True:
        user = {
            'name': user_name,
            'favorite_color': user_favorite_color,
            'favorite_number': randint(0, 1000)
        }
        producer.produce.remote(user, str(randint(0, 100)))
        sleep(1)

# end gracefully
except KeyboardInterrupt:
    for c in consumers:
        c.stop.remote()
finally:
    for c in consumers:
        c.destroy.remote()
    producer.destroy.remote()
    ray.kill(producer)