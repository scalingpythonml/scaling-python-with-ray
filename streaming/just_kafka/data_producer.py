from confluent_kafka import Producer
from uuid import uuid4
import json

# Optional per-message delivery callback (triggered by poll() or flush())
# when a message has been successfully delivered or permanently
# failed delivery (after retries).
def delivery_callback(err, msg):
    if err:
        print('Message failed delivery: ', err)
    else:
        print('Message delivered to topic ', msg.topic(), ' partition ', msg.partition(), ' offset', msg.offset())

# Producer configuration
# See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
conf = {'bootstrap.servers': 'localhost:9092'}

producer = Producer(**conf)

user_name = 'john'
user_favorite_color = 'blue'

# Read lines from stdin, produce each line to Kafka
for user_favorite_number in range(100):
    try:
        # Produce message
        user = {
            'name': user_name,
            'favorite_color': user_favorite_color,
            'favorite_number': user_favorite_number
        }
        data = json.dumps(user).encode('UTF8')
        key = str(uuid4()).encode('UTF8')
        producer.produce(topic='test', value=data, key=key, callback=delivery_callback)

    except BufferError:
        print(f'Local producer queue is full {len(producer)} messages awaiting delivery: try again\n')

    # Serve delivery callback queue.
    # NOTE: Since produce() is an asynchronous API this poll() call
    #       will most likely not serve the delivery callback for the
    #       last produce()d message.
    producer.poll(0)

producer.flush()



