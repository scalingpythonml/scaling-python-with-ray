# Simple implementation of heater

from time import sleep
from random import randint

from streaming.shared.kafka_support import setup_topics
from streaming.shared.kafka_support import KafkaProducer
from streaming.shared.kafka_support import KafkaConsumer
from streaming.shared.heater_implementation import BaseHeater
from streaming.shared.heater_implementation import temperatureUpRate
from streaming.shared.heater_implementation import temperatureDownRate
from streaming.shared.heater_implementation import tempInterval
from streaming.shared.heater_implementation import controlInterval

server = 'localhost:9092'

heaterinputtopic = "heatercontrol"
heatersourcegroup = "HeaterControlGroup",

heateroutputtopic = "sensor"
thermostattopic = "thermostat"

print(f"Starting Heater: kafka: {server} sending sensor data to topic: {heateroutputtopic}")
print(f"Temperature up rate: {temperatureUpRate} temperature down rate: {temperatureDownRate}")
print(f"Sensor publish interval: {tempInterval} control change interval: {controlInterval}")

# Heater class
class Heater(BaseHeater):
    # initialize heater
    def __init__(self, id: str, producer: KafkaProducer, current: float = 42.0, desired: float = 45.0, upDelta: float = 1.0, downDelta: float = 1.0,
                 temptopic: str = heateroutputtopic):

        super().__init__(id=id, current=current, desired=desired, upDelta=upDelta, downDelta=downDelta)
        self.temptopic = temptopic
        self.producer = producer


    # Submit current temperature
    def submit_temperature(self, timeInterval: int = tempInterval):
        super().submit_temperature()
        # Publish it
        data = {'measurement': self.current}
        print(f'Submitting measurement {data} with key {self.id}')
        self.producer.produce(topic=self.temptopic, data=data, key=self.id)

    # update desired temperature
    def submit_desired(self):
        data = {'temperature' : self.desired, 'up_delta' : self.upDelta, 'down_delta': self.downDelta}
        print('Submitting desired temperature ', data, ' with key ', self.id)
        self.producer.produce(topic=self.temptopic, data=data, key=self.id)
        self.desired = self.desired + randint(0, 10) - 5.0

# Setuo Kafka
setup_topics(topics=[heaterinputtopic, heateroutputtopic, thermostattopic])

# Create objects
producer = KafkaProducer()
heater = Heater(id='1234', producer=producer)
reciever = KafkaConsumer(topic=heaterinputtopic, callback=heater.process_control, group=heatersourcegroup)
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