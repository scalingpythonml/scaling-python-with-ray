import ray
import json
from time import sleep
from random import seed
from random import randint

def setup_kafka(server: str = 'localhost:9092', topic: str = 'test', partitions: int = 10, replication: int = 1):
    # Recreate topic
    from confluent_kafka.admin import AdminClient, NewTopic
    admin = AdminClient({'bootstrap.servers': server})

    # Delete topics
    fs = admin.delete_topics([topic])

    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic ", topic, " is deleted")
        except Exception as e:
            print("Failed to delete topic ", topic, " error ", e)

    # Wait to make sure topic is deleted
    sleep(5)
    # Call create_topics to asynchronously create topics.
    fs = admin.create_topics([NewTopic(topic, num_partitions=partitions, replication_factor=replication)])

    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic ", topic, " is created")
        except Exception as e:
            print("Failed to create topic ", topic, " error ", e)

@ray.remote
class KafkaProducer:
    def __init__(self, server: str = 'localhost:9092', topic: str = 'test'):
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

@ray.remote
class KafkaConsumer:
    def __init__(self, group: str = 'ray', server: str = 'localhost:9092', topic: str = 'test', restart: str = 'latest'):
        from confluent_kafka import Consumer
        from ray.streaming import StreamingContext
        from uuid import uuid4
        # Configuration
        consumer_conf = {'bootstrap.servers': server,   # bootstrap server
                 'group.id': group,                      # group ID
                 'session.timeout.ms': 6000,            # session tmout
                 'auto.offset.reset': restart}          # restart

        # Create Consumer instance
        self.consumer = Consumer(consumer_conf)
        self.topic = topic
        self.id = str(uuid4())
        self.ctx = StreamingContext.Builder().build()

    def start(self):
        self.run = True
        def print_assignment(consumer, partitions):
            print('Consumer ', self.id)
            print('Assignment:', partitions)

        def getmessages()-> dict :
            while self.run:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print("Consumer error: ", msg.error())
                    continue
                else:
                    # Proper message
                    print("Consumer ", self.id, "new message: topic=", msg.topic(), ' partition=', msg.partition(),
                          ' offset=', msg.offset(), ' key=', msg.key().decode('UTF8'))
                    value = json.loads(msg.value().decode('UTF8'))
                    print(value)
                    return value

        # Subscribe to topics
        self.consumer.subscribe([self.topic], on_assign = print_assignment)
        self.ctx.source(getmessages()).set_parallelism(1) \
            .filter(lambda x: x['favorite_number'] > 10) \
            .sink(lambda x: print("filtered result", x))
        self.ctx.submit("kafka_sample")

    def stop(self):
        self.run = False

    def destroy(self):
        self.consumer.close()

# Setup Kafka
setup_kafka()

# Setup rundom number generator
seed(1)

# Start Ray
ray.init(ignore_reinit_error=True)

# Start consumers and producers
n_consumers = 5     # Number of consumers
consumers = [KafkaConsumer.remote() for _ in range(n_consumers)]
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