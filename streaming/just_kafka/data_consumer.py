from confluent_kafka import Consumer, KafkaException
import json

# Configuration
consumer_conf = {'bootstrap.servers': 'localhost:9092',   # bootstrap server
                'group.id': 'test',                        # group ID
                'session.timeout.ms': 6000,                # session tmout
                'auto.offset.reset': "latest"}             # restart where we set of


# Create Consumer instance
consumer = Consumer(consumer_conf)

def print_assignment(consumer, partitions):
    print('Assignment:', partitions)

# Subscribe to topics
consumer.subscribe(['test'], on_assign=print_assignment)


# Read messages from Kafka, print to stdout
try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        else:
            # Proper message
            print("New message: topic=", msg.topic(), ' partition=', msg.partition(), ' offset=', msg.offset(), ' key=', msg.key().decode('UTF8'))
            print(json.loads(msg.value().decode('UTF8')))

except KeyboardInterrupt:
    print('Aborted by user\n')

finally:
    # Close down consumer to commit final offsets.
    consumer.close()
