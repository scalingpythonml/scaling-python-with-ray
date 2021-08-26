# Simple implementation of heater

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
from confluent_kafka import Consumer
import json
from threading import Thread
from time import sleep

from random import seed
from random import randint

server = 'localhost:9092'

heaterinputtopic = "heatercontrol"
heatersourcegroup = "HeaterControlGroup",

heateroutputtopic = "sensor"
thermostattopic = "thermostat"

temperatureUpRate = 60      # sec
temperatureDownRate = 120   # sec

tempInterval = 10           # sec
controlInterval = 600       # sec

print("Starting Heater: kafka: ", server, " sending sensor data to topic: ", heateroutputtopic)
print("Temperature up rate: ", temperatureUpRate, " temperature down rate: ", temperatureDownRate)
print("Sensor publish interval: ", tempInterval, " control change interval: ", controlInterval)

def setup_kafka(topics: [], server: str = 'localhost:9092', partitions: int = 10, replication: int = 1):
    # Recreate topic
    admin = AdminClient({'bootstrap.servers': server})

    # Delete topics
    fs = admin.delete_topics(topics)

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
    new_topics = [NewTopic(topic, num_partitions=partitions, replication_factor=replication) for topic in topics]
    fs = admin.create_topics(new_topics)

    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic ", topic, " is created")
        except Exception as e:
            print("Failed to create topic ", topic, " error ", e)

# Kafka Producer class
class KafkaProducer:
    # initialize producer
    def __init__(self, server: str = 'localhost:9092'):
        conf = {'bootstrap.servers': server}
        self.producer = Producer(**conf)

    # Send message
    def produce(self, topic: str, data: dict):
        # this is a delivery callback for kafka producer
        def delivery_callback(err, msg):
            if err:
                print('Message failed delivery: ', err)
            else:
                print('Message delivered to topic ', msg.topic(), ' partition ', msg.partition(), ' offset', msg.offset())

        self.producer.produce(topic=topic, value=json.dumps(data).encode('UTF8'),  callback=delivery_callback)
        self.producer.poll(0)

    # Destroy producer
    def destroy(self):
        self.producer.flush(30)

# Print assignment for consumer
def print_assignment(consumer, partitions):
    print('Assignment:', partitions)

# Heater class
class Heater:
    # initialize heater
    def __init__(self, id: str, producer: KafkaProducer, current: float = 42.0, desired: float = 45.0, upDelta: float = 1.0, downDelta: float = 1.0,
                 temptopic: str = heateroutputtopic):

        self.id = id

        self.current = current
        self.desired = desired

        self.upDelta = upDelta
        self.downDelta = downDelta

        self.temptopic = temptopic

        if(desired > current):
            self.command = 0
        else:
            self.command = 1

        self.producer = producer

        seed(1)


    # Submit current temperature
    def submit_temperature(self, timeInterval: int = tempInterval):
        # Update temperature
        if self.command == 0:   # Heater is on - increase temperature
           self.current = self.current + timeInterval/temperatureUpRate
        else:                   # Heater is off - decrease temperature
            self.current = self.current - timeInterval/temperatureDownRate

        # Publish it
        data = {'id': self.id, 'measurement': self.current}
        print('Submitting measurement ', data)
        self.producer.produce(topic=self.temptopic, data=data)

    # update desired temperature
    def submit_desired(self):
        data = {'id': self.id, 'temperature' : self.desired, 'up_delta' : self.upDelta, 'down_delta': self.downDelta}
        print('Submitting desired temperature ', data)
        self.producer.produce(topic=self.temptopic, data=data)
        self.desired = self.desired + randint(0, 10) - 5.0

    # Process new controller command
    def process_control(self, control: dict):
        self.command = control['control']

# Threaded Kafka consumer class
class KafkaConsumer(Thread):
    # Initialize consumer
    def __init__(self, topic: str, heater: Heater, group: str, server: str = 'localhost:9092', restart: str = 'latest'):
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
        self.heater = heater

    def run(self):
        self.run = True
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
                print("New message: from topic=", msg.topic(), ' partition=', msg.partition(), ' offset=', msg.offset())
                value = json.loads(msg.value().decode('UTF8'))
                print(value)
                self.heater.process_control(value)

    def stop(self):
        self.run = False

    def destroy(self):
        self.consumer.close()

# Setuo Kafka
setup_kafka([heaterinputtopic, heateroutputtopic, thermostattopic])

# Create objects

# Create an object of Thread
producer = KafkaProducer()
heater = Heater(id='1234', producer=producer)
reciever = KafkaConsumer(topic=heaterinputtopic, heater=heater, group=heatersourcegroup)
reciever.start()

ntemp = int(controlInterval/tempInterval)

try:
    heater.submit_desired()
    while True:
        for _ in range(ntemp):
            heater.submit_temperature()
            sleep(tempInterval)
        heater.submit_desired()
# end gracefully
except KeyboardInterrupt:
    reciever.stop()
finally:
    reciever.join()
    reciever.destroy()