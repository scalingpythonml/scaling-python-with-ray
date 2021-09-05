from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer
from time import sleep
import json
from threading import Thread


def setup_topics(server: str = 'localhost:9092', topics: [] = ['test'], partitions: int = 10, replication: int = 1):
    # Recreate topic
    # Wait for operation completion method
    def wait_for_operation_completion(futures: dict, success: str, failure: str):
        for topic, f in futures.items():
            try:
                f.result()  # The result itself is None
                print(f"Topic {topic} {success}")
            except Exception as e:
                print(f"{failure} {topic} error {e}")

    admin = AdminClient({'bootstrap.servers': server})

    # Delete topics
    fs = admin.delete_topics(topics)

    # Wait for each operation to finish.
    wait_for_operation_completion(fs, " is deleted", "Failed to delete topic ")

    # Wait to make sure topic is deleted
    sleep(3)
    # Call create_topics to asynchronously create topics.
    new_topics = [NewTopic(topic, num_partitions=partitions, replication_factor=replication) for topic in topics]
    fs = admin.create_topics(new_topics)

    # Wait for each operation to finish.
    wait_for_operation_completion(fs, " is created", "Failed to create topic ")

# Kafka Producer class
class KafkaProducer:
    # initialize producer
    def __init__(self, server: str = 'localhost:9092'):
        # Print assignment for consumer
        def print_assignment(consumer, partitions):
            print(f'Assignment: {partitions}')
        conf = {'bootstrap.servers': server}
        self.producer = Producer(**conf)

    # Send message
    def produce(self, topic: str, data: dict, key: str=None):
        # this is a delivery callback for kafka producer
        def delivery_callback(err, msg):
            if err:
                print(f'Message failed delivery: {err}')
            else:
                print(f'Message delivered to topic {msg.topic()} partition {msg.partition()} offset {msg.offset()}')

        kkey = None
        if key != None:
            kkey = key.encode('UTF8')

        self.producer.produce(topic=topic, value=json.dumps(data).encode('UTF8'),  key=kkey, callback=delivery_callback)
        self.producer.poll(0)

    # Destroy producer
    def destroy(self):
        self.producer.flush(30)

# Threaded Kafka consumer class
class KafkaConsumer(Thread):
    # Initialize consumer
    def __init__(self, topic: str, callback, group: str, server: str = 'localhost:9092', restart: str = 'latest'):
        # Call the Thread class's init function
        Thread.__init__(self)
        # Configuration
        consumer_conf = {'bootstrap.servers': server,   # bootstrap server
                         'group.id': group,             # group ID
                         'session.timeout.ms': 6000,    # session tmout
                         'auto.offset.reset': restart}  # restart

        # Create Consumer instance
        self.consumer = Consumer(consumer_conf)
        self.topic = topic
        self.callback = callback

    def run(self):
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
                print("Consumer error: ", msg.error())
                continue
            else:
                # Proper message
                print(f"New message: topic={msg.topic()}  partition= {msg.partition()} offset={msg.offset()}")
                if msg.key() != None:
                    print(f'key={msg.key().decode("UTF8")}')
                print(f'value = {json.loads(msg.value().decode("UTF8"))}')
                self.callback(msg)

    def stop(self):
        self.run = False

    def destroy(self):
        self.consumer.close()
