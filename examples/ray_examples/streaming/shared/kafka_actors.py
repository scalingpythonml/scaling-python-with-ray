import ray
import json

@ray.remote
class KafkaProducer:
    def __init__(self, server: str = 'localhost:9092', topic: str = 'heatercontrol'):
        from confluent_kafka import Producer
        conf = {'bootstrap.servers': server}
        self.producer = Producer(**conf)
        self.topic = topic

    def produce(self, data: dict, key: str = None):

        def delivery_callback(err, msg):
            if err:
                print(f'Message failed delivery: {err}')
            else:
                print(F'Message delivered to topic {msg.topic()} partition {msg.partition()}'
                      F' offset {msg.offset()}')

        kkey = None
        if key != None:
            kkey = key.encode('UTF8')
        self.producer.produce(topic=self.topic, value=json.dumps(data).encode('UTF8'),
                              key=kkey, callback=delivery_callback)
        self.producer.poll(0)

    def destroy(self):
        self.producer.flush(30)

class BaseKafkaConsumer:
    def __init__(self, group: str = 'ray', server: str = 'localhost:9092', topic: str = 'sensor',
                 restart: str = 'earliest'):
        from confluent_kafka import Consumer
        # Configuration
        consumer_conf = {'bootstrap.servers': server,   # bootstrap server
                         'group.id': group,                      # group ID
                         'session.timeout.ms': 6000,            # session tmout
                         'auto.offset.reset': restart}          # restart

        # Create Consumer instance
        self.consumer = Consumer(consumer_conf)
        self.topic = topic
        self.callback = None

    def start(self):
        self.run = True
        def print_assignment(consumer, partitions):
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
                print(f"New message: topic={msg.topic()}  partition= {msg.partition()} "
                      f"offset={msg.offset()}")
                key = None
                if msg.key() != None:
                    key = msg.key().decode("UTF8")
                    print(f'key={key}')
                value = json.loads(msg.value().decode("UTF8"))
                print(f'value = {value}')
                if self.callback == None:
                    print('Mo callback defined, skipping message')
                else:
                    self.callback(key, value)

    def stop(self):
        self.run = False

    def destroy(self):
        self.consumer.close()
